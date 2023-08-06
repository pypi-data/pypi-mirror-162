import os
import shutil
import re
import bisect
from datetime import date
from enum import Enum
from kabaret import flow
from kabaret.flow_entities.entities import Entity
from libreflow.baseflow.film import Film as BaseFilm
from libreflow.utils.os import zip_folder

from .shot import Shots


class ShotState(Enum):

    MISSING_FILE                = 0
    FIRST_DELIVERY              = 1  # First delivery
    NEW_TAKE_PACK_SELECTED      = 5  # New take + resend pack
    NEW_TAKE_PACK_UNSELECTED    = 6
    RESEND_TAKE_PACK_SELECTED   = 11 # Resend last take + resend pack
    RESEND_TAKE_PACK_UNSELECTED = 12
    ALREADY_DELIVERED           = 7
    ALREADY_RECEIVED            = 8


class ShotToSend(flow.SessionObject):

    sequence_name  = flow.Param()
    shot_name      = flow.Param()
    last_take      = flow.Param()
    target_take    = flow.Computed()

    # state          = flow.Param()
    selected       = flow.Param().ui(editor='bool')
    new_take       = flow.Param().ui(editor='bool')
    send_pack      = flow.Param().ui(editor='bool')
    # message        = flow.Param()

    _action        = flow.Parent(2)

    def get_init_state(self):
        return self._action.get_init_state(self.name())
    
    def ensure_take(self, kitsu_task_name):
        return self._action.ensure_take(
            self.name(),
            'working_file_plas',
            kitsu_task_name,
            take_name=self.target_take.get(),
            replace_take=not self.new_take.get()
        )
    
    def create_package(self, delivery_dir=None):
        self._action.create_shot_package(
            self.name(),
            self._action.task.get(),
            self.target_take.get(),
            self.send_pack.get(),
            delivery_dir,
        )
    
    def update_kitsu_status(self, kitsu_task_name, kitsu_status_name, revision_name):
        self._action.update_kitsu_status(
            self.name(),
            kitsu_task_name,
            kitsu_status_name,
            self.target_take.get(),
            revision_name
        )

    def compute_child_value(self, child_value):
        if child_value is self.target_take:
            last_take = self.last_take.get()
            if last_take is None:
                index = 1
            else:
                m = re.match(r't(\d+)', last_take)
                if m is not None:
                    index = int(m.group(1))
                    if self.new_take.get():
                        index += 1
                else:
                    index = 1
            self.target_take.set('t'+str(index))


class ShotsToSend(flow.DynamicMap):

    _action = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return ShotToSend

    def __init__(self, parent, name):
        super(ShotsToSend, self).__init__(parent, name)
        self._shot_names = None
        self._shot_cache = None
    
    def mapped_names(self, page_num=0, page_size=None):
        kitsu_status = self._action.to_send_kitsu_status.get()
        
        if self._shot_names is None:
            self._mng.children.clear()
            self._shot_names = []
            self._shot_cache = {}
            
            # Get shots ready to be sent on Kitsu
            kitsu = self.root().project().kitsu_api()
            validated_shots = kitsu.get_shots({
                self._action.task.get(): [self._action.to_send_kitsu_status.get()]
            })
            for sq, sh in validated_shots:
                n = f'{sq}{sh}'
                
                bisect.insort(self._shot_names, n)
                self._shot_cache[n] = dict(
                    sequence_name=sq,
                    shot_name=sh,
                    last_take_name=self._action.get_last_take(n)
                )
        
        return self._shot_names
    
    def touch(self):
        self._shot_names = None
        super(ShotsToSend, self).touch()
    
    def _configure_child(self, item):
        self.mapped_names()
        data = self._shot_cache[item.name()]
        item.sequence_name.set(data['sequence_name'])
        item.shot_name.set(data['shot_name'])
        item.last_take.set(data['last_take_name'])


class KitsuTaskNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        return ['L&S KEY FRAME', 'L&S ANIMATION']


class SendForValidation(flow.Action):

    FILES_BY_TASK = {
        'L&S KEY FRAME': ('takes_fix.plas', 'takes_fix', None),
        'L&S ANIMATION': ('takes_ani.plas', 'takes_ani', 'ani'),
    }

    to_send_kitsu_status = flow.Param('H TO SEND').ui(hidden=True)
    task                 = flow.SessionParam('L&S KEY FRAME', KitsuTaskNames).watched()
    task_status          = flow.Param('I Waiting For Approval').ui(hidden=True)
    target_site          = flow.Param('test2').ui(hidden=True)
    
    shots = flow.Child(ShotsToSend)

    _film = flow.Parent()

    def needs_dialog(self):
        self.message.set('<h2>Send shots for validation</h2>')
        self.task.revert_to_default()
        return True
    
    def run(self, button):
        task_name = self.task.get()
        task_status_name = self.task_status.get()
        delivery_dir = self.get_delivery_dir()

        for s in self.shots.mapped_items():
            if s.selected.get():
                take_name, source_revision_name = s.ensure_take(task_name)
                s.create_package(delivery_dir)
                s.update_kitsu_status(task_name, task_status_name, source_revision_name)

    def ensure_take(self, shot_name, working_file_name, kitsu_task_name, take_name=None, replace_take=False):
        lighting_files = self._film.shots[shot_name].tasks['lighting'].files
        file_name, file_display_name, suffix = self.FILES_BY_TASK[kitsu_task_name]
        suffix = suffix and suffix+'_' or ''
        name, ext = file_name.split('.')

        if not lighting_files.has_file(name, ext):
            take_file = lighting_files.add_file(
                name, ext,
                display_name=file_display_name,
                tracked=True,
                default_path_format='{sequence}_{shot}/{sequence}_{shot}_'+suffix+'{revision}'
            )
        else:
            take_file = lighting_files[f'{name}_{ext}']
        
        source_revision = lighting_files[working_file_name].get_head_revision()
        source_path = source_revision.get_path()

        if replace_take:
            if take_name is None:
                take = take_file.get_head_revision()
            else:
                take = take_file.get_revision(take_name)
            
            take.comment.set(f'Created from working file {source_revision.name()}')
            os.remove(take.get_path())
        else:
            if take_name is None:
                take_index = len(take_file.get_revisions().mapped_names()) + 1
                take_name = 't'+str(take_index)
            
            take = take_file.add_revision(
                name=take_name,
                comment=f'Created from working file {source_revision.name()}'
            )

        take_path = take.get_path()
        os.makedirs(os.path.dirname(take_path), exist_ok=True)
        shutil.copy2(source_path, take_path)

        lighting_files.touch()

        return take.name(), source_revision.name()
    
    def create_shot_package(self, shot_name, kitsu_task_name, take_name, include_pack=False, delivery_dir=None):
        lighting_files = self._film.shots[shot_name].tasks['lighting'].files
        delivery_files = self._film.shots[shot_name].tasks['delivery'].files
        today = date.today().strftime('%y%m%d')
        package_name = f'package_{today}'

        # Create package folder
        if not delivery_files.has_folder(package_name):
            package = delivery_files.add_folder(
                package_name,
                tracked=True,
                default_path_format='{sequence}_{shot}/package/'+today+'/{revision}'
            )
        else:
            package = delivery_files[package_name]
        
        pkg_rev = package.add_revision()
        pkg_path = pkg_rev.get_path()
        os.makedirs(pkg_path)

        # Copy working file in package folder
        file_name, file_display_name, suffix = self.FILES_BY_TASK[kitsu_task_name]
        name, ext = file_name.split('.')
        suffix = suffix and suffix+'_' or ''

        take_file = lighting_files[f'{name}_{ext}']
        take_path = take_file.get_revision(take_name).get_path()

        self.root().session().log_info(
            f'Copy take {take_path} into package {pkg_path}'
        )
        shutil.copy2(take_path, pkg_path)

        # If asked, copy pack as well
        if include_pack:
            pack_path = lighting_files['pack'].get_head_revision().get_path()
            self.root().session().log_info(
                f'Copy pack {pack_path} into package {pkg_path}'
            )
            shutil.copytree(pack_path, os.path.join(pkg_path, 'pack'))
        
        # Upload package
        current_site = self.root().project().get_current_site()
        upload_job = current_site.get_queue().submit_job(
            emitter_oid=pkg_rev.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
            job_type='Upload',
            init_status='WAITING'
        )

        sync_mgr = self.root().project().get_sync_manager()
        sync_mgr.process(upload_job)
        
        # Zip package in given delivery folder
        if delivery_dir is not None:
            pkg_name = f'{shot_name}_rouge_{suffix}{take_name}.zip'     # <shot_name>_rouge_<take_name>.zip
            delivery_pkg_path = os.path.join(
                delivery_dir, pkg_name
            )
            zip_folder(pkg_path, delivery_pkg_path)
        else:
            self.root().session().log_warning(
                f'{shot_name} {take_name} :: delivery folder {delivery_dir} not found'
            )
        
        msg = f'{shot_name} {take_name} :: package uploaded'
        
        self.root().session().log_info(msg)
    
    def update_kitsu_status(self, shot_name, kitsu_task_name, kitsu_status_name, take_name, revision_name):
        user_name = self.root().project().get_user_name()
        take_file_name = self.FILES_BY_TASK[kitsu_task_name][1]
        shot = self._film.shots[shot_name]
        task = shot.tasks['lighting']

        shot.set_task_status(
            kitsu_task_name,
            kitsu_status_name,
            comment=(
                f"**{user_name}** has submitted take **{take_name}** for validation.\n"
                f"- Created from working file **{revision_name}**\n\n"
                f"*{task.oid()}*"
            )
        )
    
    def get_init_state(self, shot_name):
        state = ShotState.MISSING_FILE
        if (
            self._film.shots[shot_name].tasks.has_mapped_name('lighting')
            and self._film.shots[shot_name].tasks['lighting'].files.has_file('working_file', 'plas')
            and not self._film.shots[shot_name].tasks['lighting'].files['working_file_plas'].is_empty()
        ):
            files = self._film.shots[shot_name].tasks['lighting'].files

            if (
                self.task.get() == 'L&S KEY FRAME'
                and (
                    not files.has_file('takes_fix', 'plas')
                    or not files['takes_fix_plas'].has_revision('t1')
                )
            ):
                state = ShotState.FIRST_DELIVERY
            else:
                today = date.today().strftime('%y%m%d')
                package_name = f'package_{today}'
                if (
                    self._film.shots[shot_name].tasks['delivery'].files.has_folder(package_name)
                    and not self._film.shots[shot_name].tasks['delivery'].files[package_name].is_empty()
                ):
                    last_package = self._film.shots[shot_name].tasks['delivery'].files[package_name].get_head_revision()
                    
                    if last_package.get_sync_status(site_name=self.target_site.get()) != 'Available':
                        state = ShotState.ALREADY_DELIVERED
                    else:
                        state = ShotState.ALREADY_RECEIVED
                else:
                    state = ShotState.NEW_TAKE_PACK_UNSELECTED
        
        return state
    
    def get_last_take(self, shot_name):
        last_take = None
        file_name, file_display_name, suffix = self.FILES_BY_TASK[self.task.get()]
        name, ext = file_name.split('.')

        if (
            self._film.shots[shot_name].tasks.has_mapped_name('lighting')
            and self._film.shots[shot_name].tasks['lighting'].files.has_file(name, ext)
        ):
            last_take = self._film.shots[shot_name].tasks['lighting'].files[f'{name}_{ext}'].get_head_revision()
            if last_take is not None:
                last_take = last_take.name()
        
        return last_take

    def get_delivery_dir(self):
        delivery_dir = self.root().project().get_current_site().delivery_dir.get()

        if delivery_dir is not None:
            today = date.today().strftime('%y%m%d')
            delivery_dir = os.path.join(delivery_dir, today)

            if os.path.isdir(delivery_dir):
                i = 2
                while os.path.isdir(f'{delivery_dir}-{i}'):
                    i += 1
                delivery_dir = f'{delivery_dir}-{i}'
            
            os.makedirs(delivery_dir, exist_ok=True)
        
        return delivery_dir
    
    def child_value_changed(self, child_value):
        if child_value is self.task:
            self.shots.touch()

    
    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.rouge.ui.package.SendShotsForValidationWidget'


class Film(BaseFilm):
    
    shots = flow.Child(Shots).ui(
        expanded=True,
        show_filter=True,
    )

    sequences = flow.Child(flow.Object).ui(hidden=True)

    send_for_validation = flow.Child(SendForValidation)
