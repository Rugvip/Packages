import sublime_plugin
import sublime


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
