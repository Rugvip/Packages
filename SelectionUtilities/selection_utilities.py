import sublime_plugin
import sublime
import re

# For inline eval
from fractions import *
from math import *
from base64 import b64encode, b64decode, urlsafe_b64encode, urlsafe_b64decode

import random

def rand(n):
    return random.randint(1, n)

import hashlib

def md5(s):
    return hashlib.md5(str(s).encode('utf-8')).hexdigest()

def sha1(s):
    return hashlib.sha1(str(s).encode('utf-8')).hexdigest()

def sha256(s):
    return hashlib.sha256(str(s).encode('utf-8')).hexdigest()

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
                if begin <= 0:
                    break
                char = self.view.substr(begin)
                if (char in ["\n", "\r"]):
                    break
                if (char in [",", ";"] and beginPar <= 0):
                    break
                if (char == "{"):
                    if (beginPar <= 0):
                        break
                    else:
                        beginPar -= 1
                if (char == "}"):
                    beginPar += 1
                if (self.view.score_selector(begin, "string") > 0):
                    begin -= 1
                    continue
                if (char in ["(", "["]):
                    if (beginPar <= 0):
                        break
                    else:
                        beginPar -= 1
                if (char in [")", "]"]):
                    beginPar += 1
                begin -= 1
            while (True):
                char = self.view.substr(end)
                if end >= end_position:
                    break
                # if (char in ["\n", "\r"]):
                #     break
                if (char in [",", ";"] and endPar <= 0):
                    break
                if (char == "}"):
                    if (endPar <= 0):
                        break
                    else:
                        endPar -= 1
                if (char == "{"):
                    endPar += 1
                if (self.view.score_selector(end, "string") > 0):
                    end += 1
                    continue
                if (char in [")", "]"]):
                    if (endPar <= 0):
                        break
                    else:
                        endPar -= 1
                if (char in ["(", "["]):
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


class SelectEachArgumentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        end_position = self.view.size()
        for sel in self.view.sel():
            commas = []
            begin = sel.a - 1
            end = sel.a
            beginPar = 0
            endPar = 0
            while (True):
                if begin <= 0:
                    break
                char = self.view.substr(begin)
                # if (char in ["\n", "\r"]):
                #     break
                if self.view.score_selector(begin, "string") > 0:
                    begin -= 1
                    continue
                if char in [",", ";"] and beginPar <= 0:
                    commas.append(begin)
                if char == "{":
                    if (beginPar <= 0):
                        break
                    else:
                        beginPar -= 1
                if char == "}":
                    beginPar += 1
                if char in ["(", "["]:
                    if (beginPar <= 0):
                        break
                    else:
                        beginPar -= 1
                if char in [")", "]"]:
                    beginPar += 1
                begin -= 1
            while (True):
                char = self.view.substr(end)
                if end >= end_position:
                    break
                # if (char in ["\n", "\r"]):
                #     break
                if (self.view.score_selector(end, "string") > 0):
                    end += 1
                    continue
                if (char in [",", ";"] and endPar <= 0):
                    commas.append(end)
                if (char == "}"):
                    if (endPar <= 0):
                        break
                    else:
                        endPar -= 1
                if (char == "{"):
                    endPar += 1
                if (char in [")", "]"]):
                    if (endPar <= 0):
                        break
                    else:
                        endPar -= 1
                if (char in ["(", "["]):
                    endPar += 1
                end += 1
            if begin < end:
                begin += 1
                while (self.view.substr(begin) in [" ", "\t"]):
                    begin += 1
                while (self.view.substr(end - 1) in [" ", "\t"]):
                    end -= 1

            commas.sort()
            for commaPos in commas:
                while begin < end and self.view.substr(begin).isspace():
                    begin += 1
                while commaPos > begin and self.view.substr(commaPos - 1).isspace():
                    commaPos -= 1
                sels.append(sublime.Region(begin, commaPos))
                begin = commaPos + 1

            while begin < end and self.view.substr(begin).isspace():
                begin += 1
            if begin != end:
                sels.append(sublime.Region(begin, end))

        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)


class ToggleMultilineCsvCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        end_position = self.view.size()
        selsAfter = []

        sels = [sel for sel in self.view.sel()]
        sels.reverse()
        for sel in sels:
            commas = []
            begin = sel.a - 1
            end = sel.a
            beginPar = 0
            endPar = 0
            while (True):
                if begin <= 0:
                    break
                char = self.view.substr(begin)
                # if (char in ["\n", "\r"]):
                #     break
                if (self.view.score_selector(begin, "string") > 0):
                    begin -= 1
                    continue
                if (char in [",", ";"] and beginPar <= 0):
                    commas.append(begin)
                if (char == "{"):
                    if (beginPar <= 0):
                        break
                    else:
                        beginPar -= 1
                if (char == "}"):
                    beginPar += 1
                if (char in ["(", "["]):
                    if (beginPar <= 0):
                        break
                    else:
                        beginPar -= 1
                if (char in [")", "]"]):
                    beginPar += 1
                begin -= 1
            while (True):
                char = self.view.substr(end)
                if end >= end_position:
                    break
                # if (char in ["\n", "\r"]):
                #     break
                if (self.view.score_selector(end, "string") > 0):
                    end += 1
                    continue
                if (char in [",", ";"] and endPar <= 0):
                    commas.append(end)
                if (char == "}"):
                    if (endPar <= 0):
                        break
                    else:
                        endPar -= 1
                if (char == "{"):
                    endPar += 1
                if (char in [")", "]"]):
                    if (endPar <= 0):
                        break
                    else:
                        endPar -= 1
                if (char in ["(", "["]):
                    endPar += 1
                end += 1
            if begin < end:
                begin += 1
            #     while (self.view.substr(begin) in [" ", "\t"]):
            #         begin += 1
            #     while (self.view.substr(end - 1) in [" ", "\t"]):
            #         end -= 1

            commas.sort()

            # find the substring of each component
            beginIt = begin
            endIt = end
            commaSeparatedValues = []
            for commaPos in commas:
                while beginIt < end and self.view.substr(beginIt).isspace():
                    beginIt += 1
                while commaPos > beginIt and self.view.substr(commaPos - 1).isspace():
                    commaPos -= 1
                commaSeparatedValues.append(self.view.substr(sublime.Region(beginIt, commaPos)))
                beginIt = commaPos + 1

            while beginIt < end and self.view.substr(beginIt).isspace():
                beginIt += 1
            while endIt < end_position and self.view.substr(endIt - 1).isspace():
                endIt -= 1
            if beginIt != end:
                commaSeparatedValues.append(self.view.substr(sublime.Region(beginIt, endIt)))

            isSameLine = self.view.line(begin) == self.view.line(end)
            inserted = None

            if isSameLine and begin != end:
                indent = self.view.substr(self.view.find('[\\t\\s]*', self.view.line(begin).begin()))
                inserted = '\n' + indent + '\t' + (',\n' + indent + '\t').join(commaSeparatedValues) + ',\n' + indent
            else:
                inserted = ', '.join(commaSeparatedValues)

            # erase + insert instead of replace so that we can keep track of size changes
            self.view.erase(edit, sublime.Region(begin, end))
            size = self.view.insert(edit, begin, inserted)

            diff = begin - end + size
            for sel in selsAfter:
                sel.a += diff
                sel.b += diff

            selsAfter.append(sublime.Region(begin, begin + size))


        self.view.sel().clear()
        for sel in selsAfter:
            self.view.sel().add(sel)


def getPosOtherLine(self, sel, up):
    beginPos = self.view.text_to_layout(sel.a)
    endPos = self.view.text_to_layout(sel.b)
    beginX = beginPos[0]
    endX = endPos[0]
    y = 0
    if (up):
        y = beginPos[1] - self.view.line_height()
    else:
        y = endPos[1] + self.view.line_height()
    begin = self.view.layout_to_text((beginX, y))
    end = self.view.layout_to_text((endX, y))
    return sublime.Region(begin, end)


class DeleteLineImprovedCommand(sublime_plugin.TextCommand):
    def run(self, edit, up):
        sels = []
        erase = []
        for sel in self.view.sel():
            removedLine = getPosOtherLine(self, sel, not up)
            erase.append(self.view.full_line(removedLine))

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
    def run_(self, edit, args):
        view = self.view
        sels = [r for r in view.sel()]
        view.sel().clear()
        view.run_command("drag_select", {'event': args['event']})
        new_sel = view.sel()
        point = new_sel[0].a
        new_sel.clear()

        strr = ""
        for sel in sels:
            if sel.contains(point):
                strr = view.substr(sel)
                sels.remove(sel)
        map(new_sel.add, sels)
        sels.reverse()
        for sel in sels:
            view.replace(edit, sel, strr)


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


class DeleteEolCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        last = []
        for sel in self.view.sel():
            for line in view.lines(sel):
                last.append(line.b)

        last.reverse()
        for line in last:
            view.erase(edit, sublime.Region(line - 1, line))


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


class AlignBySymbolDoCommand(sublime_plugin.TextCommand):
    def run(self, edit, str):
        view = self.view
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
            if pos > max:
                max = pos
        # insert spaces in front of str
        for line in lines:
            pos = view.substr(line).find(str)
            if not pos < 0:
                view.insert(edit, line.a + pos, " " * (max - pos))

        view.end_edit(edit)


class AlignBySymbolCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.end_edit(edit)

        def response(str):
            # split selection into unique lines
            view.run_command("align_by_symbol_do", {'str': str})

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


        finds = view.find_all("\\b" + esc + "\\b")

        for find in finds:
            if (sel.contains(find)):
                view.sel().add(find)


class FindAllWordsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        sel = view.sel()[0]

        subs = view.substr(sel)
        if (len(subs) < 1):
            return

        esc = "".join(map(lambda c: "\\"+str(hex(ord(c)))[1:], subs))


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


class RemoveAlphaNumCommand(sublime_plugin.TextCommand):
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
            sels.insert(0, sublime.Region(begin, end))

        for sel in sels:
            self.view.erase(edit, sel)
            right = sel.begin()
            if (right != 0):
                left = right - 1
                a = self.view.substr(left)
                b = self.view.substr(right)

                if (a == b):
                    self.view.erase(edit, sublime.Region(left, right))
                elif a in ('_', '-'):
                    self.view.erase(edit, sublime.Region(left, left + 1))
                elif b in ('_', '-'):
                    self.view.erase(edit, sublime.Region(right, right + 1))


class RemoveWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            word = self.view.word(sel.a)
            begin = sel.begin()
            end = sel.end()
            while word.a < begin:
                chars = self.view.substr(sublime.Region(begin-2, begin))
                begin -= 1
                if chars[0].islower() and chars[1].isupper() or chars[0] in ('_', '-'):
                    break
            while word.b > end:
                chars = self.view.substr(sublime.Region(end-1, end+1))
                if not chars.islower() and not chars.isupper() or chars[1] in ('_', '-'):
                    break;
                end += 1

            sels.append(sublime.Region(begin, end))

        sels.reverse()

        for sel in sels:
            just_after = sublime.Region(sel.end(), sel.end() + 2)
            next_chars = self.view.substr(just_after)
            first_char = self.view.substr(sel.begin())
            if first_char.islower() and next_chars[0].isupper() and next_chars[1].islower():
                self.view.replace(edit, just_after, next_chars.lower())

            self.view.erase(edit, sel)
            right = sel.begin()

            if (right != 0):
                left = right - 1
                a = self.view.substr(left)
                b = self.view.substr(right)

                if (a == b):
                    self.view.erase(edit, sublime.Region(left, right))



class RemoveToDelimsCommand(sublime_plugin.TextCommand):
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
            sels.insert(0, sublime.Region(begin, end))

        for sel in sels:
            self.view.erase(edit, sel);


class NullifyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sels = [r for r in view.sel()]
        sels.reverse()
        for sel in sels:
            selStr = view.substr(sel)
            line = view.full_line(sel)
            whitespace = re.match(r"\s*", view.substr(line)).group()
            if view.score_selector(sel.begin(), "source.js") > 0:
                view.insert(edit, line.end(), whitespace + selStr + " = null\n")
            else:
                view.insert(edit, line.end(), whitespace + selStr + " = NULL;\n")


class RemoveLastSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sels = view.sel()
        sels.subtract(sels[-1])


class DeleteEmptyLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sels = view.sel()
        for sel in reversed(sels):
            for line in reversed(view.lines(sel)):
                st = view.substr(line).strip()
                if not st:
                    view.erase(edit, view.full_line(line));


class ExpandSelectionVerticallyCommand(sublime_plugin.TextCommand):
    def run(self, edit, up):
        view = self.view
        sels = view.sel()
        for sel in sels:
            pos = self.view.text_to_layout(sel.b)
            y = pos[1] - self.view.line_height() * (int(up) * 2 - 1)
            if sel.xpos == -1:
                sel.xpos = self.view.text_to_layout(sel.b)[0]
            end = self.view.layout_to_text((sel.xpos, y))
            sels.subtract(sel)
            sel.b = end
            sels.add(sel)


class DuplicateBelowCommand(sublime_plugin.TextCommand):
    def run(self, edit, selection = 'after'):

        # sels = [sel for sel in self.view.sel()]
        # sels.reverse()

        new_sels = []

        for sel in self.view.sel():
            if sel.begin() == sel.end():
                sel = self.view.word(sel)
            text = self.view.substr(sel)
            line = self.view.line(sel)

            indentation = self.view.substr(self.view.find('\\s*', line.begin()))
            if self.view.substr(line.end() - 1) == '{':
                indentation += '\t'

            snippet = "\n" + indentation + text

            new_sel_point = line.end() + 1 + len(indentation)
            if selection == 'after':
                new_sel_point += len(text)

            new_sels.append(sublime.Region(new_sel_point))
            self.view.insert(edit, line.end(), snippet)

        self.view.sel().clear()
        self.view.sel().add_all(new_sels)


import os

class SwitchFileExtendedCommand(sublime_plugin.TextCommand):
    def run(self, edit, extensions):
        _, filename = os.path.split(self.view.file_name())
        if filename.endswith('.js'):
            if filename.endswith('.spec.js'):
                filename = filename.replace('.spec.js', '.js')
            else:
                filename = filename.replace('.js', '.spec.js')
            self.view.window().run_command('show_overlay', {'overlay': 'goto', 'text': filename})
            self.view.window().run_command('move', {'by': 'lines', 'forward': True})
            self.view.window().run_command('insert', {'characters': '\n'})
        else:
            self.view.window().run_command("switch_file", {'extensions': extensions})


class RunTextCommandTimesCommand(sublime_plugin.TextCommand):
    def run(self, edit, n, command, args=None):
        while n > 0:
            self.view.run_command(command, args)
            n -= 1

class RunWindowCommandTimesCommand(sublime_plugin.TextCommand):
    def run(self, edit, n, command, args=None):
        while n > 0:
            self.view.window().run_command(command, args)
            n -= 1


class ActiveViewThemeListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        settings = view.settings()

        active_scheme = settings.get("active_scheme")
        if active_scheme is None:
            print("active_scheme not set!")
            return

        settings.set("color_scheme", active_scheme)

    def on_deactivated(self, view):
        settings = view.settings()

        inactive_scheme = settings.get('inactive_scheme')
        if inactive_scheme is None:
            print("inactive_scheme not set!")
            return

        settings.set("color_scheme", inactive_scheme)


class JavaScriptFunctionSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # for each selection in view
        firsts = []
        for sel in self.view.sel():
            last = last_bracket = first = sel.end()
            # Find the last bracket
            while (self.view.substr(last) in [' ', ')', ']']):
                if (self.view.substr(last) != ' '):
                    last_bracket = last + 1
                last += 1

            if (last_bracket < last):
                last = last_bracket

            self.view.insert(edit, last, ';')
            firsts.append(first)

        self.view.sel().clear()
        for first in firsts:
            self.view.sel().add(sublime.Region(first))

        self.view.run_command("insert_snippet", {"contents": "function ($1) {\n\t$0\n}"})


class JavaScriptConsoleSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit, jsonify):

        sels = [sel for sel in self.view.sel()]
        sels.reverse()

        for sel in sels:
            if sel.begin() == sel.end():
                sel = self.view.word(sel)
            text = self.view.substr(sel)
            line = self.view.line(sel)

            indentation = self.view.substr(self.view.find('\\s*', line.begin()))
            if self.view.substr(line.end() - 1) == '{':
                indentation += '\t'

            snippet = "\n{0}console.log('{1}: ', {1})".format(indentation, text)
            if jsonify:
                snippet = "\n{0}console.log('{1}: ', JSON.stringify({1}))".format(indentation, text)
            self.view.insert(edit, line.end(), snippet)


class BashEchoSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        sels = [sel for sel in self.view.sel()]
        sels.reverse()

        for sel in sels:
            if sel.begin() == sel.end():
                sel = self.view.word(sel)
            text = self.view.substr(sel)
            line = self.view.line(sel)

            indentation = self.view.substr(self.view.find('\\s*', line.begin()))
            if self.view.substr(line.end() - 1) == '{':
                indentation += '\t'

            snippet = '\n{0}echo "{1}: ${{{1}}}"'.format(indentation, text)
            self.view.insert(edit, line.end(), snippet)


class GoLogSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        sels = [sel for sel in self.view.sel()]
        sels.reverse()

        for sel in sels:
            if sel.begin() == sel.end():
                sel = self.view.word(sel)
            text = self.view.substr(sel)
            line = self.view.line(sel)

            indentation = self.view.substr(self.view.find('\\s*', line.begin()))
            if self.view.substr(line.end() - 1) == '{':
                indentation += '\t'

            snippet = '\n{0}fmt.Printf("{1}: %+v\\n", {1})'.format(indentation, text)
            self.view.insert(edit, line.end(), snippet)


class GoMemberSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = [sel for sel in self.view.sel()]
        sels.reverse()

        count = 0
        # List of all function declarations in the file
        func_name_regions = self.view.find_by_selector('entity.name.function.go')

        for sel in sels:
            # Find the closes function declaration above our point
            func_name_region = None
            for region in func_name_regions:
                if region.end() < sel.begin():
                    func_name_region = region
                else:
                    break
            if func_name_region is None:
                continue

            func_to_point = self.view.substr(sublime.Region(func_name_region.end(), sel.begin()))
            # heh
            func_to_point = func_to_point.replace('interface{}', '')
            score = 0
            left_zero = False

            # Figure out if our point is inside the function
            for c in func_to_point:
                if c == '{':
                    score += 1
                    if score > 0:
                        left_zero = True
                elif c == '}':
                    score -= 1
                    if score == 0 and left_zero:
                        func_name_region = None
                        break
            if func_name_region is None:
                continue

            func_kw_search = func_name_region.begin()
            func_kw_region = None
            while True:
                end = self.view.find_by_class(func_kw_search, False, sublime.CLASS_WORD_END)
                start = self.view.find_by_class(end, False, sublime.CLASS_WORD_START)
                func_kw_search = start
                reg = sublime.Region(start, end)
                s = self.view.substr(reg)
                if s == "":
                    break
                if s == "func":
                    func_kw_region = reg
                    break

            if func_kw_region is None:
                continue

            func_target = self.view.substr(sublime.Region(func_kw_region.end(), func_name_region.begin())).strip()
            func_target
            match = re.match("\\(\\s*(\\w+)[^)]+\\)", func_target)

            if match is None:
                continue

            target_name = match.group(1)

            self.view.insert(edit, sel.begin(), target_name + ".")
            count += 1

        if count == 1:
            self.view.run_command("auto_complete")


class LuaPrintSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        sels = [sel for sel in self.view.sel()]
        sels.reverse()

        for sel in sels:
            if sel.begin() == sel.end():
                sel = self.view.word(sel)
            text = self.view.substr(sel)
            line = self.view.line(sel)

            indentation = self.view.substr(self.view.find('\\s*', line.begin()))
            if self.view.substr(line.end() - 1) == '{':
                indentation += '\t'

            snippet = "\n{0}print('{1}: '..tostring({1}))".format(indentation, text)
            self.view.insert(edit, line.end(), snippet)


class JavaScriptMemberSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = [sel for sel in self.view.sel()]
        sels.reverse()

        for sel in sels:
            if sel.begin() == sel.end():
                sel = self.view.word(sel)
            text = self.view.substr(sel)
            line = self.view.line(sel)

            indentation = self.view.substr(self.view.find('\\s*', line.begin()))
            if self.view.substr(line.end() - 1) == '{':
                indentation += '\t'

            snippet = "\n{0}this._{1} = {1}".format(indentation, text)
            self.view.insert(edit, line.end(), snippet)



class SortAndUniqueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("sort_lines", {"case_sensitive": False})
        self.view.run_command("permute_lines", {"operation": "unique"})


class ToggleFirstCase(sublime_plugin.TextCommand):
    def run(self, edit):
        sel = self.view.sel()[0]

        sels = []
        for sel in self.view.sel():
            pos = sel.a
            while (self.view.substr(pos - 1).isalnum()):
                pos -= 1
            if self.view.substr(pos).isalnum():
                sels.append(sublime.Region(pos, pos + 1))

        for sel in sels:
            char = self.view.substr(sel)
            if char.isupper():
                char = char.lower()
            else:
                char = char.upper()
            self.view.replace(edit, sel, char)


class JavaScriptConstructorSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        class_sels = self.view.find_by_selector('meta.class.js')

        sel = self.view.sel()[0]
        class_str = None

        for class_sel in class_sels:
            class_sel = self.view.expand_by_class(class_sel, sublime.CLASS_LINE_START | sublime.CLASS_LINE_END)
            if class_sel.contains(sel):
                class_str = self.view.substr(class_sel)
                break
        else:
            return

        sel_first_line = self.view.line(class_sel.begin() + 1)
        sel_line = self.view.line(sel.begin())

        indentation = self.view.substr(self.view.find('\\s*', sel_first_line.begin()))
        first_line = self.view.substr(sel_first_line)

        has_super = ' extends ' in first_line
        has_component = ' extends Component' in first_line or ' extends React.Component' in first_line
        snippet = None

        self.view.sel().clear()
        self.view.sel().add(sel_line.end())

        self.view.insert(edit, sel_line.end(), '\n')

        if has_component:
            snippet = '{0}\tconstructor(props) {{\n\t\tsuper(props)\n\t\t$0\n\t}}'.format(indentation)
        elif has_super:
            snippet = '{0}\tconstructor($1) {{\n\t\tsuper($2)$3\n\t}}'.format(indentation)
        else:
            snippet = '{0}\tconstructor($1) {{\n\t\t$2\n\t}}'.format(indentation)

        self.view.run_command('insert_snippet', {
            'contents': snippet
        })


class SelectClipboardCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        clipboard = sublime.get_clipboard().split('\n')
        sels = self.view.sel()
        sel_size = sum(sel.end() - sel.begin() for sel in sels)

        found = []

        for clipboard_line in clipboard:
            results = self.view.find_all(clipboard_line, sublime.LITERAL)

            if sel_size > 0:
                for result in results:
                    for sel in sels:
                        if sel.contains(result):
                            found.append(result)
                            break
            else:
                found += results

        self.view.sel().clear()
        self.view.sel().add_all(found)


# This needs to be bound to a 'press_command'
class RemoveSelectionCommand(sublime_plugin.TextCommand):
    # Need to override run_ instead of run to get access to the mouse event
    def run_(self, edit, args):
        sels = self.view.sel()

        # Save old sels, must be extracted into a new list
        old_sels = [sel for sel in sels]
        # Clear current sel, drag_select on existing sels doesn't work
        sels.clear()

        # Ignore args other than the mouse event
        self.view.run_command('drag_select', {'event': args['event']})
        click_point = sels[0].a

        # Clear the click point selection and restore old selection except for click_point
        sels.clear()
        for old_sel in old_sels:
            if not old_sel.contains(click_point):
                sels.add(old_sel)


class ClipboardFlipCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        clipboard = sublime.get_clipboard()

        sels = [s for s in self.view.sel()]
        sels.reverse()
        for sel in sels:
            current = self.view.substr(sel)
            self.view.replace(edit, sel, clipboard)
            sublime.set_clipboard(current)


class CommaJoinLines(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        last = []
        for sel in self.view.sel():
            for line in view.lines(sel):
                last.append(line.b)

        last.reverse()
        for line in last:
            if view.substr(line - 1) != ',':
                view.insert(edit, line, ',')

        self.view.run_command('join_lines')

