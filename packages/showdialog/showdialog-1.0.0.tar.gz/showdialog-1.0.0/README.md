# showdialog
Simple module for showing GTK dialog.

## Install
```bash
pip install showdialog
```

## Usage

### showdialog.show_msg(title, text, sectext, btns, msgtype)
Opens GTK MessageDialog

#### Args
title (`str`): Dialog caption
text (`Union[Tuple[Optional[str], bool], Optional[str]]`): Dialog primary text, str or tuple `(text, use_markup)`
sectext (`Union[Tuple[Optional[str], bool], Optional[str]]`, optional): Dialog secondary text, str or tuple. Defaults to `None`.
btns (`Gtk.ButtonsType`, optional): Dialog buttons. Defaults to `Gtk.ButtonsType.OK`.
msgtype (`Gtk.MessageType`, optional): Dialog message type. Defaults to `Gtk.MessageType.INFO`.

#### Example:
```python
from showdialog import show_msg
show_msg(title='', text='Hello world!')
```
