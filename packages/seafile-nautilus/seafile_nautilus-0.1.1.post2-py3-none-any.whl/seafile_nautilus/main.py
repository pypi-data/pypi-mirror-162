#!/usr/bin/env python3
import argparse
import gettext
import locale
import os
import sys
from enum import Enum
from typing import List, Union, Literal
# import logging
# logging.basicConfig(level=logging.DEBUG)

from seafile_nautilus.__version__ import __version__
from seafile_nautilus.pyzenity import Zenity
from seafile_nautilus.seafile import SeafileAccount, FileNotSyncedError, SeafileConfigFileMissing, SyncedElement, \
    Permissions

script_real_path = os.path.dirname(os.path.realpath(__file__))
localedir = os.path.join(script_real_path, 'locales')
current_locale, encoding = locale.getdefaultlocale()
tr = gettext.translation('messages', localedir=localedir, languages=[current_locale], fallback=True)
tr.install()
# _ = gettext.gettext


class Button(str, Enum):
    create_share_link = _("Create share link")
    create_upload_link = _("Create upload link")
    delete_share_link = _("Delete share link")
    delete_upload_link = _("Delete upload link")
    set_share_link_permissions = _("Change share link permissions")
    link_perm_none = _("Preview Only")
    link_perm_down = _("Preview and download")
    link_perm_down_edit = _("Edit on cloud and download")
    link_perm_down_up = _("Download and upload")
    details = _("Details")
    detail_share_link = _("Details about the share link")
    detail_upload_link = _("Details about the upload link")
    detail_internal_link = _("Details about the internal link")
    see_on_cloud = _("See on cloud")
    quit = _("Quit")


def _not_synced(file: str) -> None:
    """Displays an error message because file is not part of any seafile synchronized library.

    :param file: file or folder name
    """
    Zenity.warning(_("Error"),
                   _("« {href_file} »\n\ndoes not belong to "
                     "any synchronized library.").format(href_file=href(file)))


def _file_does_not_exist(file: str) -> None:
    """Displays an error message because file does not exist locally.

    :param file: the wrong file path
    """
    Zenity.warning(_("Error"),
                   _("« {file} »\nis not valid a valid path.").format(file=file))


def _config_file_missing(file: str) -> None:
    """Displays an error message because one seafile config file could not be found.

    :param file: the wrong file path
    """
    Zenity.warning(_("Error"),
                   _("One part of seafile local configuration data is missing:\n{file}\n"
                     "\n"
                     "Are you sure Seafile is correctly installed for the current user?").format(file=file))


def _nautilus_selected_files() -> List[str]:
    """Returns the content of the environment variable named 'NAUTILUS_SCRIPT_SELECTED_FILE_PATHS'
    which is set by Nautilus before calling a script.

    :return: the list of the paths to the selected files/folders.
    """
    try:
        return (os.environ['NAUTILUS_SCRIPT_SELECTED_FILE_PATHS'].strip('\n')).split('\n')
    except KeyError:
        return []


def head(text: str, w: int = 15, color: str = None) -> str:
    ret = f"<tt><b>{text.rjust(w)}</b></tt>"
    if color:
        return f"<span color=\"{color}\">{ret}</span>"
    return ret


def href(link: Union[str, None]) -> str:
    """ Returns an HTML hyperlink if link is a URL or a path to a local file/folder.
    Otherwise, returns an empty string.

    :return: HTML hyperlink
    """
    if isinstance(link, str):
        if link.startswith('http'):
            return f'<a href="{link}">{link}</a>'
        if os.path.exists(link):
            return f'<a href="file://{link}">{link}</a>'
        else:
            return link
    if link is None:
        return ''


def are_you_sure_delete_link(kind: Literal['share', 'upload'], short_name: str) -> bool:
    """Prompts user to confirm (share or upload) link deletion.

    :param kind: 'share' or 'upload' string according to the kind of link to delete.
    :param short_name: file basename or folder name
    :return: True if user accepts.
    """
    if kind not in ('share', 'upload'):
        return False
    title = _('Delete {kind} link ?').format(kind=kind)
    text = _("Are you sure you want to delete the {kind} link?\n\n"
             "The link to « {short_name} » will be <b>immediately and permanently "
             "invalidated</b>.\n"
             "You cannot undo this action.\n"
             "If you create a new link, it will be different from the current one.").format(
        kind=kind, short_name=short_name)
    return Zenity.question(title=title,
                           text=text,
                           default_cancel=True)


def display_details(element: SyncedElement) -> None:
    """Pops up a Zenity dialog asking the user to choose the type of link for which they want to have details.
    Then, opens a new Zenity window with the requested details.

    :param element: a SyncedElement object pointing to the file/folder.
    """
    choices = list()
    if element.get_share_link_url():
        choices.append(Button.detail_share_link)
    if element.get_internal_link_url():
        choices.append(Button.detail_internal_link)
    if element.get_upload_link_url():
        choices.append(Button.detail_upload_link)

    rep = Zenity.choice(choices,
                        title=element.short_name,
                        text=_("About which link would you like details?"))
    if rep == Button.detail_share_link:
        details = element.get_share_link_details()
        text = (head('Share link: ') + ' ' +
                _("any user who has access to the links can access the files or folders pointed by the link.") + '\n' +
                head('') + _("No login is required.") + "\n"
                )
        height = 560
    elif rep == Button.detail_internal_link:
        details = element.get_internal_link_details()
        text = (head('Internal link: ') + ' ' +
                _("only logged in users who have share permissions to file or folder can access this link.") + '\n' +
                head('') + _("Login is required.") + '\n' +
                head('') + _("Each file/folder has such a link that cannot be deleted.") + "\n"
                )
        height = 250
    elif rep == Button.detail_upload_link:
        details = element.get_upload_link_details()
        text = (head('Upload link: ') + ' ' +
                _("any user who has access to the links can upload files to the folder pointed by the link.") + '\n' +
                head('') + _("No login is required.") + "\n"
                )
        height = 420
    else:
        return
    extra_button = {'extra_button': Button.set_share_link_permissions.value} if rep == Button.detail_share_link else {}
    re = Zenity.list(title=_("Details about the link to « {short_name} »").format(short_name=element.short_name),
                     text=text,
                     width=800, height=height,
                     columns=[_('Field'), _('Value')],
                     table=list(details.__dict__.items()),
                     check_output=True,
                     **extra_button)
    if re == Button.set_share_link_permissions:
        set_share_link_permissions(element)


def available_permissions(synced_elt: SyncedElement) -> List[Button]:
    """This function returns a list of availbale permissions regarding a synchronized element.

    :param synced_elt: a 'SyncedElement' object
    :return: a list of 'Button's
    """
    choices = [Button.link_perm_down, Button.link_perm_none,
               Button.link_perm_down_up, Button.link_perm_down_edit]
    if not synced_elt.isdir:
        choices.remove(Button.link_perm_down_up)
    if synced_elt.isdir or not synced_elt.file_details.can_edit:
        choices.remove(Button.link_perm_down_edit)
    return choices


def current_permissions(synced_elt: SyncedElement) -> Button:
    """

    :param synced_elt:
    :return:
    """
    details = synced_elt.get_share_link_details()
    curr_perm = details.permissions
    if curr_perm.can_upload:
        return Button.link_perm_down_up
    elif curr_perm.can_edit:
        return Button.link_perm_down_edit
    elif curr_perm.can_download:
        return Button.link_perm_down
    else:
        return Button.link_perm_none


def chose_link_permissions(synced_elt: SyncedElement):
    choices = available_permissions(synced_elt)
    p = Zenity.choice(choices=choices,
                      title=_("Share « {file_name} »").format(file_name=synced_elt.short_name),
                      text=_("Please, set access permission to share link."))
    return Permissions(can_edit=(p == Button.link_perm_down_edit),
                       can_download=(p in (Button.link_perm_down, Button.link_perm_down_up)),
                       can_upload=(p == Button.link_perm_down_up))


def set_share_link_permissions(synced_elt: SyncedElement):
    curr_perm = current_permissions(synced_elt)
    choices = available_permissions(synced_elt)

    p = Zenity.choice(choices=choices,
                      title=_("Modification of share link permissions on « {short_name} »").format(
                          short_name=synced_elt.short_name),
                      text=_("Current permissions are: <b>{curr_perm}</b>.\n\n"
                             "Click on <b>« {curr_perm} »</b> to leave the link permissions unchanged.\n"
                             "Click on any other button to change permissions.\n"
                             "Permission changes can be undone.").format(
                          curr_perm=curr_perm))
    new_perm = Permissions(can_edit=(p == Button.link_perm_down_edit),
                           can_download=(p in (Button.link_perm_down,
                                               Button.link_perm_down_up,
                                               Button.link_perm_down_edit)),
                           can_upload=(p == Button.link_perm_down_up))
    synced_elt.set_share_link_permissions(new_perm)


def chose_function_loop(synced_elt: SyncedElement) -> None:
    """
    Main menu loop. The window shows a link to the local file/folder and the links (smart, internal and
    upload) when they exist. The user is asked to choose something to do among: 1. show link details, 2. create/delete
    a share link, 3. create/delete an upload link, 4. see in the cloud, 5. quit.
    :param synced_elt: a SyncedElement object pointing to the file/folder.
    """
    share_url = synced_elt.get_share_link_url()
    internal_url = synced_elt.get_internal_link_url()
    upload_url = synced_elt.get_upload_link_url()
    choices = list()
    choices.append(Button.details)
    if share_url:
        choices.append(Button.delete_share_link)
    else:
        choices.append(Button.create_share_link)
    if upload_url:
        choices.append(Button.delete_upload_link)
    elif synced_elt.isdir:
        choices.append(Button.create_upload_link)
    choices.append(Button.see_on_cloud)
    choices.append(Button.quit)
    rep = Zenity.choice(choices,
                        title=synced_elt.short_name,
                        text='<tt>' + '\n'.join(
                            [head(_("Local link:")) + " " + href(synced_elt.file) + '\n',
                             head("Share link:") + " " + href(share_url),
                             head("Internal link:") + " " + href(internal_url),
                             head("Upload link:", color="gray" if not synced_elt.isdir else None) + " " +
                             href(upload_url)]) + "</tt>",
                        width=800)

    if rep == Button.create_share_link:
        perm = chose_link_permissions(synced_elt)
        synced_elt.create_share_link(permissions=perm)
    elif rep == Button.create_upload_link:
        synced_elt.create_upload_link()
    elif rep == Button.delete_share_link:
        if are_you_sure_delete_link('share', synced_elt.short_name):
            synced_elt.delete_share_link()
    elif rep == Button.delete_upload_link:
        if are_you_sure_delete_link('upload', synced_elt.short_name):
            synced_elt.delete_upload_link()
    elif rep == Button.see_on_cloud:
        synced_elt.show_on_cloud()
        sys.exit(0)
    elif rep == Button.details:
        display_details(synced_elt)
    elif rep == Button.quit:
        sys.exit(0)
    elif rep == "":
        sys.exit(0)
    else:
        pass
    chose_function_loop(synced_elt)


def main(*args):
    print("This is seafile_nautilus version", __version__)
    print()
    # 'main' can be called from nautilus (args are retrieved from environment variable)
    if nautilus_files := _nautilus_selected_files():
        print("I was called from Nautilus")
        if len(nautilus_files) > 1:
            Zenity.warning(_("Error"),
                           _("You must select <b>exactly one</b> file or folder."))
            sys.exit(1)
        else:
            file = nautilus_files[0]
    # 'main' can be called from python directly with args
    elif args:
        if len(args) != 1:
            print(_("The script takes exactly one file/folder path as argument."))
            sys.exit(1)
        else:
            file = args[0]
    # 'main' can be called from bin entrypoint (args are retrieved from argparse)
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("file",
                            help="path to some folder",
                            nargs='+',
                            type=os.path.abspath)
        parser.add_argument('-v', '--version',
                            action='version',
                            version=__version__)
        p_args = parser.parse_args()
        if len(p_args.file) != 1:
            print(_("The script takes exactly one file/folder path as argument."))
            sys.exit(1)
        else:
            file = p_args.file[0]

    try:
        account = SeafileAccount()
    except SeafileConfigFileMissing as e:
        _config_file_missing(e.file)
        sys.exit(-1)
    try:
        synced_elt = SyncedElement(account, file)
    except FileNotSyncedError:
        _not_synced(file)
        sys.exit(-1)
    except FileNotFoundError:
        _file_does_not_exist(file)
        sys.exit(-1)
    chose_function_loop(synced_elt)


if __name__ == '__main__':
    main()
