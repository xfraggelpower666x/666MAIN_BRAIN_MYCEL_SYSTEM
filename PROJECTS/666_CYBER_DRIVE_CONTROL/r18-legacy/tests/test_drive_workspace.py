from types import SimpleNamespace
import json
from klrw.drive_workspace import Workspace, enumerate_drives, stable_volume_key, exact_io_map, DriveInfo


def test_seed_selection_and_persistence(tmp_path):
    path=tmp_path/'folder'/'prefs.json'
    state=Workspace(path)
    d=DriveInfo('volume:id-01','C:','WINDOWS','','NTFS')
    assert state.preferences(d)=={'tray':True,'overlay':True,'keyboard':False}
    state.preferences(d)['tray']=False
    state.data['overlay'].update(x=345,y=562,locked=True)
    state.save()
    other=Workspace(path)
    assert other.preferences(d)['tray'] is False
    assert other.data['overlay']['locked'] is True
    assert other.data['overlay']['x']==345


def test_new_usb_default_off_unless_seed(tmp_path):
    workspace=Workspace(tmp_path/'prefs.json')
    drive=DriveInfo('volume:usb-01','Q:','External',r'\\.\PhysicalDrive3','NTFS')
    assert workspace.preferences(drive)=={'tray':False,'overlay':False,'keyboard':False}
    workspace.save()
    assert Workspace(workspace.path).preferences(drive)==workspace.preferences(drive)


def test_no_guess_of_volume_to_disk_io():
    drive=DriveInfo('volume:abc','C:','Windows','C:','NTFS')
    assert exact_io_map([drive],{'PhysicalDrive0'})=={}
    assert exact_io_map([drive],{'C:'})=={'volume:abc':'C:'}


def test_enumeration_dedup_and_label():
    class P:
        def disk_partitions(self,all=False):
            return [SimpleNamespace(mountpoint='C:\\',device='C:',fstype='NTFS',opts='rw'),
                    SimpleNamespace(mountpoint='D:\\',device='D:',fstype='NTFS',opts='removable')]
    drives=enumerate_drives(P(),guid_reader=lambda m:'GUID-'+m,label_reader=lambda m:'LABEL-'+m)
    assert [d.mount for d in drives]==['C:','D:']
    assert drives[1].removable
    assert drives[0].label=='LABEL-C:'


def test_corrupt_file_does_not_destroy_default(tmp_path):
    path=tmp_path/'prefs.json';path.write_text('broken',encoding='utf8')
    obj=Workspace(path)
    assert obj.data['letter_preferences']['A:']['overlay'] is True


def test_reject_poisoned_coordinate(tmp_path):
    path=tmp_path/'prefs.json'
    path.write_text(json.dumps({'schema':1,'overlay':{'x':'bad','y':99999,'alpha':20,'size':100,'locked':True}}))
    obj=Workspace(path)
    assert obj.data['overlay']['x']==110
    assert obj.data['overlay']['y']==110
    assert obj.data['overlay']['locked'] is True
