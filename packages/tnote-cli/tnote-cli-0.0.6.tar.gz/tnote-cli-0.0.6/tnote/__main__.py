
import os
import click
from tnote.note_module import Note
from tnote.func_module import index_check, print_index, get_file, recent_check, NOTESPATH, INDEXPATH


@click.command()
@click.argument("note_id", required=False)
@click.argument("path", required=False, type=click.Path(readable=True, writable=True, dir_okay=False))
@click.option('--recent', '-r', is_flag=True, show_default=True, default=False, help='Uses most recent note with any other option')
@click.option("--edit", "-e", 'edit', is_flag=True, default=False, help="Default action, creates the note if one doesn't exist and then opens an editor")
@click.option("--view", "-v", 'view', is_flag=True, default=False, help='View a note rendering any Markdown in the process')
@click.option("--delete", "-d", 'delete', is_flag=True, default=False, help='Delete a note')
@click.option('--change_id', '-i', 'change_id', help='Changes the note ID, to change the filename use -m')
@click.option("--move", "-m", 'move', type=click.Path(readable=True, writable=True, dir_okay=False), help='Allows you to move a note to the specified path')
@click.option('--execute', '-x', count=True, help=' -x : Execute the file if executable, -xx : Make file executable and execute it if user has permissions')
def cli(**k):
    """
    NOTE_ID : This is what you will use as a name for the note and to access it in the future.\n
    PATH : Only used when creating a note, specify the path to the note, if none specified will go in the default notes folder.
    """
    index = get_file(INDEXPATH)
    if k['recent']:
        k['note_id'] = recent_check(index)

    if k['note_id'] == None:
        print_index()
        return

    if not k['edit']:
        action = False
        for key, value in k.items():
            if key not in ['recent', 'path', 'note_id', 'edit'] and value:
                action = True
        k['edit'] = not action

    path = \
        index_check(index, k['note_id'], k['move']) or \
        k['path'] or \
        os.path.join(NOTESPATH, k['note_id']+'.md')

    note = Note(id=k['note_id'], path=path)

    if k['delete']:
        note.delete_note()
        return

    if k['change_id']:
        note.change_id(k['change_id'])

    if k['move']:
        note.move_note(k['move'])

    if k['edit']:
        note.edit_note()

    if k['execute'] >= 2:
        note.exe(True)
        return

    if k['execute'] == 1:
        note.exe(False)
        return

    if k['view']:
        note.view_note()


if __name__ == '__main__':
    cli()
