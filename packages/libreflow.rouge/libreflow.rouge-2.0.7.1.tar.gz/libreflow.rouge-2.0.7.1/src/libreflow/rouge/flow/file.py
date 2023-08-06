import os
import shutil
import pathlib

from kabaret import flow
from libreflow.baseflow.file import (
    TrackedFile            as BaseTrackedFile,
    TrackedFolder          as BaseTrackedFolder,
    Revision               as BaseRevision,
    TrackedFolderRevision  as BaseTrackedFolderRevision,
    FileSystemMap          as BaseFileSystemMap,
    CreateWorkingCopyAction as BaseCreateWorkingCopyAction,
    PublishFileAction      as BasePublishFileAction,
    RevisionsWorkingCopiesChoiceValue,
)
from libreflow.utils.flow import get_contextual_dict


class Revision(BaseRevision):
    
    def get_path(self, relative=False):
        path = self.path.get()

        if path == '' or path is None:
            raise Exception((
                f'Cannot call get_path() on revision {self.oid()} '
                 'since its path is undefined.'
            ))

        if not relative:
            root = self.root().project().get_root(
                user_workspace=self.working_copy.get()
            )
            path = os.path.join(root, path)
        
        return path


class TrackedFolderRevision(BaseTrackedFolderRevision):
    pass


class RevisionsWorkingCopies(RevisionsWorkingCopiesChoiceValue):

    _files = flow.Parent(3)
    _shot = flow.Parent(6)

    def _fill_ui(self, ui):
        ui['hidden'] = (
            self._shot.get_task_status('L&S ANIMATION') == 'K APPROVED'
            or not self._files.has_folder('pack')
            or self._files['pack'].get_head_revision() is None
            or self._files['pack'].get_head_revision().get_sync_status() != 'Available'
        )


class CreateWorkingCopyAction(BaseCreateWorkingCopyAction):

    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)

    from_revision = flow.Param(None, RevisionsWorkingCopies).ui(
        label='Revision'
    )

    _shot = flow.Parent(5)

    def get_buttons(self):
        status = self._shot.get_task_status('L&S ANIMATION')
        if status == 'K APPROVED':
            self.message.set((
                '<h3>Create a working copy</h3>'
                '<font color=#D5000D>You can\'t create a working '
                'copy since the status of the <b>L&S ANIMATION</b> '
                'task is <b>APPROVED</b>.</font>'
            ))
            return ['Cancel']
        elif (
            not self._files.has_folder('pack')
            or self._files['pack'].get_head_revision() is None
            or self._files['pack'].get_head_revision().get_sync_status() != 'Available'
        ):
            self.message.set((
                '<h3>Create a working copy</h3>'
                '<font color=#D5000D>You can\'t create a working '
                'copy since no <b>pack</b> folder has been prepared '
                'for this shot.</font>'
            ))
            return ['Cancel']
        else:
            return super(CreateWorkingCopyAction, self).get_buttons()
    
    def run(self, button):
        super(CreateWorkingCopyAction, self).run(button)

        if button == 'Create' or button == 'Create from scratch':
            # Copy pack into user workspace if not copied yet
            self._ensure_pack_in_workspace()

            # Update Kitsu status of the current task
            user_name = self.root().project().get_user_name()

            if self._shot.get_task_status('L&S KEY FRAME') != 'K APPROVED':
                target_task = 'L&S KEY FRAME'
            else:
                target_task = 'L&S ANIMATION'

            self._shot.set_task_status(
                target_task,
                'E Work In Progress',
                comment=(
                    f"**{user_name}** has created a working copy on "
                    f"'{self._task.name()}/{self._file.display_name.get()}'."
                )
            )
    
    def _ensure_pack_in_workspace(self):
        # Retrieve the path of the pack in the user workspace
        pack = self._files['pack']
        working_dir = self.root().project().get_root(user_workspace=True)
        pack_relpath = pack.get_head_revision().get_path(relative=True)
        path_in_workspace = os.path.join(working_dir, pack_relpath)

        if not os.path.isdir(path_in_workspace):
            path_on_site = os.path.join(self.root().project().get_root(), pack_relpath)
            shutil.copytree(path_on_site, path_in_workspace)


class KitsuTaskNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    STRICT_CHOICES = False

    _task = flow.Parent(4)

    def choices(self):
        kitsu = self.root().project().kitsu_api()
        tm = self.root().project().get_task_manager()
        subtasks = tm.get_subtasks(self._task.name())

        return [
            kitsu.get_task_name(self._task.name(), st)
            for st in subtasks
        ]
    
    def revert_to_default(self):
        current = self._task.current_subtask.get()
        kitsu = self.root().project().kitsu_api()
        if current:
            kitsu_task = kitsu.get_task_name(self._task.name(), current)
            self.set(kitsu_task)
        else:
            names = self.choices()
            if names:
                self.set(names[0])


class KitsuTargetStatus(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    _statutes = {
        'WIP': 'E Work In Progress',
        'To check': 'F To CHECK ',
    }

    def choices(self):
        return ['WIP', 'To check']
    
    def get_kitsu_status(self):
        return self._statutes[self._value]


class PublishFileAction(BasePublishFileAction):

    keep_editing = flow.SessionParam(False).ui(
        editor='bool',
        hidden=True,
    )
    upload_after_publish = flow.SessionParam(False).ui(
        editor='bool',
        hidden=True,
    )
    status = flow.SessionParam('WIP', KitsuTargetStatus).ui(
        label='Kitsu status'
    )

    _file = flow.Parent()
    _task = flow.Parent(3)
    _shot = flow.Parent(5)

    def check_default_values(self):
        self.comment.apply_preset()
    
    def update_presets(self):
        self.comment.update_preset()

    def run(self, button):
        if button == 'Cancel':
            return
        
        # Keep working copy when Kitsu status is set to WIP
        self.keep_editing.set(
            self.status.get() == 'WIP'
        )

        super(PublishFileAction, self).run(button)
        
        user_name = self.root().project().get_user_name()

        key_frame_status = self._shot.get_task_status('L&S KEY FRAME')
        target_task = 'L&S KEY FRAME'

        if key_frame_status == 'K APPROVED':
            target_task = 'L&S ANIMATION'

        self._shot.set_task_status(
            target_task,
            self.status.get_kitsu_status(),
            comment=(
                f"**{user_name}** has published version **{self._file.get_head_revision().name()}**.\n"
                f"> {self.comment.get()}\n\n"
                f"*{self._task.oid()}*"
            )
        )


class SendFileForValidation(flow.Action):

    _file = flow.Parent()
    _map  = flow.Parent(2)
    _shot = flow.Parent(5)
    _film = flow.Parent(7)

    kitsu_target_task   = flow.SessionParam(value_type=KitsuTaskNames).watched()
    send_pack           = flow.SessionParam(False).ui(editor='bool')
    kitsu_source_status = flow.Param('H TO SEND').ui(hidden=True)
    kitsu_target_status = flow.Param('I Waiting For Approval').ui(hidden=True)

    def allow_context(self, context):
        return (
            context
            and self._file.name() == 'working_file_plas'
            and not self._file.is_empty()
        )
    
    def needs_dialog(self):
        self.kitsu_target_task.revert_to_default()
        return True

    def get_buttons(self):
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        elif not self._is_status_valid():
            return self.get_result(close=False)
        
        send_for_validation = self._film.send_for_validation
        delivery_dir = send_for_validation.get_delivery_dir()

        take_name, source_revision_name = send_for_validation.ensure_take(
            self._shot.name(),
            'working_file_plas',
            self.kitsu_target_task.get(),
            replace_take=False
        )
        send_for_validation.create_shot_package(
            self._shot.name(),
            self.kitsu_target_task.get(),
            take_name,
            include_pack=self.send_pack.get(),
            delivery_dir=delivery_dir
        )
        send_for_validation.update_kitsu_status(
            self._shot.name(),
            self.kitsu_target_task.get(),
            self.kitsu_target_status.get(),
            take_name, source_revision_name
        )
    
    def child_value_changed(self, child_value):
        if child_value is self.kitsu_target_task:
            self._check_kitsu_status()
            self.send_pack.set((
                self.kitsu_target_task.get() == 'L&S KEY FRAME'
                and (
                    not self._map.has_file('takes_fix', 'plas')
                    or not self._map['takes_fix_plas'].has_revision('t1')
                )
            ))
    
    def _is_status_valid(self):
        kitsu_task_name = self.kitsu_target_task.get()
        source_status = self.kitsu_source_status.get()

        return self._shot.get_task_status(kitsu_task_name) == source_status
    
    def _check_kitsu_status(self):
        if not self._is_status_valid():
            self.message.set((
                '<font color=#D5000D>'
                'You cannot send this file for validation since '
                f'its Kitsu status is not <b>{self.kitsu_source_status.get()}</b>.'
                '</font>'
            ))
        else:
            self.message.set('')


class TrackedFile(BaseTrackedFile):
    
    to_validate = flow.Child(SendFileForValidation)


class TrackedFolder(BaseTrackedFolder):
    pass


class FileSystemMap(BaseFileSystemMap):
    
    def add_file(self, name, extension, display_name=None, base_name=None, tracked=False, default_path_format=None):
        if default_path_format is None:
            default_path_format = get_contextual_dict(self, 'settings').get(
                'path_format', None
            )
        return super(FileSystemMap, self).add_file(name, extension, display_name, base_name, tracked, default_path_format)

    def add_folder(self, name, display_name=None, base_name=None, tracked=False, default_path_format=None):
        if default_path_format is None:
            default_path_format = get_contextual_dict(self, 'settings').get(
                'path_format', None
            )
        return super(FileSystemMap, self).add_folder(name, display_name, base_name, tracked, default_path_format)
