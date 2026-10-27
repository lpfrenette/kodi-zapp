import xbmcgui


class GroupDialog(xbmcgui.WindowXMLDialog):
    """Edits a draft selection; only Valider commits it to the caller."""

    def __init__(self, *args, **kwargs):
        self.groups = []
        self.counts = {}
        self.checked = set()
        self.result = None

    def label(self, index):
        name = self.groups[index]
        return '{}  {}  ({} chaînes)'.format('[x]' if index in self.checked else '[ ]', name, self.counts[name])

    def update_count(self):
        self.getControl(110).setLabel('{} / {} groupes cochés — OK pour cocher ou décocher'.format(len(self.checked), len(self.groups)))

    def redraw(self):
        listing = self.getControl(100)
        position = listing.getSelectedPosition()
        listing.reset()
        listing.addItems([xbmcgui.ListItem(self.label(i)) for i in range(len(self.groups))])
        if self.groups:
            listing.selectItem(max(0, min(position, len(self.groups) - 1)))
        self.update_count()

    def onInit(self):
        self.redraw()

    def onClick(self, control_id):
        if control_id == 100:
            listing = self.getControl(100)
            index = listing.getSelectedPosition()
            if 0 <= index < len(self.groups):
                if index in self.checked:
                    self.checked.remove(index)
                else:
                    self.checked.add(index)
                listing.getListItem(index).setLabel(self.label(index))
                self.update_count()
        elif control_id == 101:
            self.checked = set(range(len(self.groups)))
            self.redraw()
        elif control_id == 102:
            self.checked.clear()
            self.redraw()
        elif control_id == 103:
            self.result = sorted(self.checked)
            self.close()
        elif control_id == 104:
            self.close()

    def onAction(self, action):
        if action.getId() in (9, 10, 92):
            self.close()


def select_groups(addon_path, groups, counts, selected):
    dialog = GroupDialog('groups.xml', addon_path, 'Default', '1080i')
    dialog.groups = groups
    dialog.counts = counts
    dialog.checked = set(selected)
    dialog.doModal()
    result = dialog.result
    del dialog
    return result
