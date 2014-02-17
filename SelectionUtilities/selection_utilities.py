import sublime_plugin
import sublime
import re
from math import *


class SplitSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            sels.append(sel.a)
            sels.append(sel.b)

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sublime.Region(sel))


class DeleteInwardsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for sel in self.view.sel():
            if sel.a + 1 == sel.b:
                self.view.erase(edit, sel)
            elif sel.a != sel.b:
                self.view.erase(edit, sublime.Region(sel.b-1, sel.b))
                self.view.erase(edit, sublime.Region(sel.a, sel.a+1))


class DeleteOutwardsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for sel in self.view.sel():
            if sel.a + 1 == sel.b:
                self.view.erase(edit, sel)
            elif sel.a != sel.b:
                self.view.erase(edit, sublime.Region(sel.b, sel.b + 1))
                self.view.erase(edit, sublime.Region(sel.a - 1, sel.a))


class MoveSelectionInwardsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            if sel.a + 1 >= sel.b:
                sels.append(sublime.Region(sel.a, sel.a))
            else:
                sels.append(sublime.Region(sel.a + 1, sel.b - 1))

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)


class MoveSelectionOutwardsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            sels.append(sublime.Region(sel.a - 1, sel.b + 1))

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)


class SplitAndSelectLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            sels.append(self.view.lines(sel))

        self.view.sel().clear()
        for sel in sels:
            for line in sel:
                self.view.sel().add(line)


class SelectToDelimsCommand(sublime_plugin.TextCommand):
    def run(self, edit, delims):
        sels = []
        end_position = self.view.size()
        for sel in self.view.sel():
            begin = sel.a - 1
            end = sel.b
            while (self.view.substr(begin) not in delims and begin > 0):
                begin -= 1
            while (self.view.substr(end) not in delims and end < end_position):
                end += 1
            if (begin < end and begin > 0):
                begin += 1
            sels.append(sublime.Region(begin, end))

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)


class SelectAlphaNumCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            begin = sel.a - 1
            end = sel.b
            while (self.view.substr(begin).isalnum()):
                begin -= 1
            while (self.view.substr(end).isalnum()):
                end += 1
            if begin < end:
                begin += 1
            sels.append(sublime.Region(begin, end))

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)


class SelectArgumentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        end_position = self.view.size()
        for sel in self.view.sel():
            begin = sel.a - 1
            end = sel.b
            beginPar = 0
            endPar = 0
            while (True):
                if (self.view.score_selector(begin, "string") > 0):
                    begin -= 1
                    continue
                if begin <= 0:
                    break
                char = self.view.substr(begin)
                if (char in ["\n", "\r"]):
                    break
                if (char in [",", ";"] and beginPar <= 0):
                    break
                if (char in ["(", "{", "["]):
                    if (beginPar <= 0):
                        break
                    else:
                        beginPar -= 1
                if (char in [")", "}", "]"]):
                    beginPar += 1
                begin -= 1
            while (True):
                if (self.view.score_selector(end, "string") > 0):
                    end += 1
                    continue
                char = self.view.substr(end)
                if end >= end_position:
                    break
                # if (char in ["\n", "\r"]):
                #     break
                if (char in [",", ";"] and endPar <= 0):
                    break
                if (char in [")", "}", "]"]):
                    if (endPar <= 0):
                        break
                    else:
                        endPar -= 1
                if (char in ["(", "{", "["]):
                    endPar += 1
                end += 1
            if begin < end:
                begin += 1
                while (self.view.substr(begin) in [" ", "\t"]):
                    begin += 1
                while (self.view.substr(end - 1) in [" ", "\t"]):
                    end -= 1
            sels.append(sublime.Region(begin, end))

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)


def getPosOtherLine(self, sel, direction):
    beginPos = self.view.text_to_layout(sel.a)
    endPos = self.view.text_to_layout(sel.b)
    beginX = beginPos[0]
    endX = endPos[0]
    y = 0
    if (direction == "up"):
        y = beginPos[1] - self.view.line_height()
    else:
        y = endPos[1] + self.view.line_height()
    begin = self.view.layout_to_text((beginX, y))
    end = self.view.layout_to_text((endX, y))
    return sublime.Region(begin, end)


class DeleteLineImprovedCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction):
        sels = []
        erase = []
        for sel in self.view.sel():
            sels.append(getPosOtherLine(self, sel, direction))
            erase.append(self.view.full_line(sel))

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)

        erase.reverse()
        for e in erase:
            self.view.erase(edit, e)


class MoveSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction, extend):
        sels = []
        for sel in self.view.sel():
            if extend and (direction == "up" or direction == "down"):
                sels.append(sel)
            beginPos = self.view.text_to_layout(sel.a)
            endPos = self.view.text_to_layout(sel.b)

            if direction == "up":
                beginPos = beginPos[0], beginPos[1] - self.view.line_height()
                endPos = endPos[0], endPos[1] - self.view.line_height()
            if direction == "down":
                beginPos = beginPos[0], beginPos[1] + self.view.line_height()
                endPos = endPos[0], endPos[1] + self.view.line_height()
            if direction == "left":
                if not extend:
                    beginPos = self.view.text_to_layout(sel.a - 1)
                endPos = self.view.text_to_layout(sel.b - 1)
            if direction == "right":
                if not extend:
                    beginPos = self.view.text_to_layout(sel.a + 1)
                endPos = self.view.text_to_layout(sel.b + 1)

            begin = self.view.layout_to_text(beginPos)
            end = self.view.layout_to_text(endPos)
            sels.append(sublime.Region(begin, end))

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)


class CopyToSelectionsCommand(sublime_plugin.TextCommand):
    def run_(self, args):
        view = self.view
        sels = [r for r in view.sel()]
        view.sel().clear()
        view.run_command("drag_select", {'event': args['event']})
        new_sel = view.sel()
        point = new_sel[0].a
        new_sel.clear()

        str = ""
        for sel in sels:
            if sel.contains(point):
                str = view.substr(sel)
                sels.remove(sel)
        edit = view.begin_edit()
        map(new_sel.add, sels)
        sels.reverse()
        for sel in sels:
            view.replace(edit, sel, str)
        view.end_edit(edit)


class TransposeLineByLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        lines = []
        sels = [sel for sel in view.sel()]
        for sel in sels:
            line = view.line(sel.a)
            if all(l.a != line.a and l.b != line.b for l in lines):
                lines.append(view.line(sel.a))

        lines.reverse()
        sels.reverse()
        for line in lines:
            trans = []
            for sel in sels:
                if line.contains(sel):
                    trans.append(sel)
            first = view.substr(trans[0])
            for i in range(1, len(trans)):
                view.replace(edit, trans[i - 1], view.substr(trans[i]))
            view.replace(edit, trans[-1], first)
            del trans
            del first
        del lines
        del sels


class SinglifySelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit, all):
        sels = []
        for sel in self.view.sel():
            sels.append(sel.b)
        self.view.sel().clear()
        if all:
            self.view.sel().add(sublime.Region(sels[0]))
        else:
            for sel in sels:
                self.view.sel().add(sublime.Region(sel))


class ToggleCharAtEndCommand(sublime_plugin.TextCommand):
    def run(self, edit, char):
        view = self.view
        last = []
        for sel in self.view.sel():
            for line in view.lines(sel):
                last.append(line.b)

        last.reverse()
        for line in last:
            if view.substr(line - 1) == char:
                view.erase(edit, sublime.Region(line - 1, line))
            else:
                view.insert(edit, line, char)


class ToggleCharAtEndExceptLastCommand(sublime_plugin.TextCommand):
    def run(self, edit, char):
        view = self.view
        last = []
        for sel in self.view.sel():
            for line in view.lines(sel):
                last.append(line.b)

        last.reverse()
        for line in last[1:]:
            if view.substr(line - 1) == char:
                view.erase(edit, sublime.Region(line - 1, line))
            else:
                view.insert(edit, line, char)


class FlipSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = [s for s in self.view.sel()]
        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sublime.Region(sel.b, sel.a))


class AlignBySymbolCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.end_edit(edit)

        def response(str):
            # split selection into unique lines
            edit = view.begin_edit()
            lines = []
            sels = [sel for sel in view.sel()]
            for sel in sels:
                for line in view.lines(sel):
                    if all(l.a != line.a and l.b != line.b for l in lines):
                        lines.append(line)
            lines.reverse()
            # find rightmost str
            max = 0
            for line in lines:
                pos = view.substr(line).find(str)
                print(pos)
                if pos > max:
                    max = pos
            # insert spaces in front of str
            for line in lines:
                pos = view.substr(line).find(str)
                if not pos < 0:
                    view.insert(edit, line.a + pos, " " * (max - pos))

            view.end_edit(edit)

        view.window().show_input_panel("Enter alignment string:", "", response, None, None)


class InsertNumbersCommand(sublime_plugin.TextCommand):
    def run(self, edit, offset):
        view = self.view

        sels = [sel for sel in view.sel()]
        i = len(sels) - 1 + int(offset)
        sels.reverse()
        for sel in sels:
            view.replace(edit, sel, str(i))
            i -= 1


class EvalPythonCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        sels = [sel for sel in view.sel()]
        sels.reverse()
        for sel in sels:
            view.replace(edit, sel, str(eval(view.substr(sel))))


class RefactorCommand(sublime_plugin.WindowCommand):
    def run(self):
        win = self.window

        view = win.active_view()
        file = view.file_name()
        if not file[-2] == '.':
            return

        for f in win.views():
            fn = f.file_name()
            if fn[0:-2] == file[0:-2] and fn[-1] != file[-1]:
                hview = f

        sel = view.sel()[0]
        subs = view.substr(sel)

        def response(str):
            edit = view.begin_edit()
            view.replace(edit, sel, str)
            view.end_edit(edit)

            hedit = hview.begin_edit()
            finds = hview.find_all(subs, sublime.LITERAL)
            finds.reverse()
            for r in finds:
                hview.replace(hedit, r, str)
            hview.end_edit(hedit)

        win.show_input_panel("Rename " + subs + ":", "", response, None, None)


class RefactorScope(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        sel = view.sel()[0]

        subs = view.substr(sel)
        if (len(subs) < 1):
            return

        end_position = self.view.size()

        begin = sel.begin()
        end = sel.end()
        beginPar = 0
        endPar = 0
        while (True):
            if (self.view.score_selector(begin, "string") > 0):
                begin -= 1
                continue
            if begin <= 0:
                break
            char = self.view.substr(begin)
            if (char == "{"):
                if (beginPar <= 0):
                    break
                else:
                    beginPar -= 1
            if (char == "}"):
                beginPar += 1
            begin -= 1
        while (True):
            if (self.view.score_selector(end, "string") > 0):
                end += 1
                continue
            char = self.view.substr(end)
            if end >= end_position:
                break
            if (char == "}"):
                if (endPar <= 0):
                    break
                else:
                    endPar -= 1
            if (char == "{"):
                endPar += 1
            end += 1
        if begin < end:
            begin += 1

        sel = sublime.Region(begin, end)

        esc = "".join(map(lambda c: "\\"+str(hex(ord(c)))[1:], subs))

        print(esc)

        finds = view.find_all("\\b" + esc + "\\b")

        for find in finds:
            if (sel.contains(find)):
                view.sel().add(find)


class FindAllWordsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        sel = view.sel()[0]

        subs = view.substr(sel)
        print(subs)
        if (len(subs) < 1):
            return

        esc = "".join(map(lambda c: "\\"+str(hex(ord(c)))[1:], subs))

        print(esc)

        finds = view.find_all("\\b" + esc + "\\b")

        for find in finds:
            view.sel().add(find)

class ConvertCamelCaseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sels = [r for r in view.sel()]
        sels.reverse()

        for sel in sels:
            str = view.substr(sel)

            if str.islower():
                str = str.title().replace("_", "")
            else:
                str = re.sub(r"([A-Z])", "_\\1", str)
                str = re.sub(r"^_", "", str).lower()

            view.replace(edit, sel, str)


class AutoSemiColonForceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Loop through and add the semi colon
        for sel in self.view.sel():
            # The last letter we've dealt with
            first = sel.end()
            self.view.insert(edit, first, ';')

        # Loop through and add move it to the end
        for sel in self.view.sel():
            last = last_bracket = first = sel.end()
            # Find the last bracket
            while (self.view.substr(last) in [' ', ')', ']', "'", '"']):
                if (self.view.substr(last) != ' '):
                    last_bracket = last + 1
                last += 1

            if (last_bracket < last):
                last = last_bracket

            # Can we insert the semi colon elsewhere?
            if last > first:
                self.view.erase(edit, sublime.Region(first - 1, first))
                # Delete the old semi colon
                self.view.insert(edit, last - 1, ';')
                # Move the cursor
                self.view.sel().clear()
                self.view.sel().add(sublime.Region(last, last))


class RemoveArgumentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sels = [r for r in view.sel()]
        sels.reverse()
        end_position = self.view.size()
        for sel in sels:
            begin = sel.a - 1
            end = sel.b
            beginPar = 0
            endPar = 0
            beginComma = False
            while (True):
                if (self.view.score_selector(begin, "string") > 0):
                    begin -= 1
                    continue
                if begin <= 0:
                    break
                char = self.view.substr(begin)
                if (char in ["\n", "\r"]):
                    break
                if (char in [";"] and beginPar <= 0):
                    break
                if (char in [","] and beginPar <= 0):
                    beginComma = True
                    begin -= 1
                    break
                if (char in ["(", "{", "["]):
                    if (beginPar <= 0):
                        break
                    else:
                        beginPar -= 1
                if (char in [")", "}", "]"]):
                    beginPar += 1
                begin -= 1
            while (True):
                if (self.view.score_selector(end, "string") > 0):
                    end += 1
                    continue
                char = self.view.substr(end)
                if end >= end_position:
                    break
                # if (char in ["\n", "\r"]):
                #     break
                if (char in [";"] and endPar <= 0):
                    break
                if (char in [","] and endPar <= 0):
                    if not beginComma:
                        end += 1
                    break
                if (char in [")", "}", "]"]):
                    if (endPar <= 0):
                        break
                    else:
                        endPar -= 1
                if (char in ["(", "{", "["]):
                    endPar += 1
                end += 1
            if begin < end:
                begin += 1
                while (self.view.substr(begin) in [" ", "\t"]):
                    begin += 1
                while (self.view.substr(end) in [" ", "\t"]):
                    end += 1
            self.view.erase(edit, sublime.Region(begin, end))


class NullifyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sels = [r for r in view.sel()]
        sels.reverse()
        for sel in sels:
            str = view.substr(sel)
            line = view.full_line(sel);
            whitespace = re.match(r"\s*", view.substr(line)).group()
            view.insert(edit, line.end(), whitespace + str + " = NULL;\n")

class RemoveLastSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sels = view.sel()
        sels.subtract(sels[-1])
