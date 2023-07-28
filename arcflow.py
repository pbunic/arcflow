#!/usr/bin/python3

"""
Single file program that works with python standard library.
It's nice to pair with drop-down terminal like yakuake. Main purpose is to keep
short-term task objectives terminal accessible, perfect for your project design
guidelines and similar stuff.

written by: Predrag Bunic (2023)
github url: github.com/pbunic/arcflow
license: GPL v3
"""

import os
import sys
import shutil
import json
import argparse
from datetime import datetime


user_home = os.path.expanduser("~")
directory = os.path.join(user_home, ".arcflow")
json_storage = os.path.join(directory, "storage.json")
current_date = datetime.now().strftime("%d-%b-%Y").upper()


##############
# PREPARATIONS
##############
class Host:
    """
    Class for os-level corruption detections.
    """
    def __init__(self):
        self.term_list = [
            # If you have terminal emulator that supports ansi escape
            # sequences not listed below --- you can add it here.
            "xterm", "xterm-16color", "xterm-256color",
        ]

        try:
            self._files_state()
        except PermissionError as exc:
            print(f"ERROR: {exc}")
            sys.exit(1)

        try:
            self._terminal_width()
        except ValueError as exc:
            print(f"ERROR: {exc}")
            sys.exit(1)

        self.ansi_support = self._ansi_support()

    def _files_state(self, path_dir=directory, path_json=json_storage):
        """
        File (directory and json file) should exist and have RW permissions.
        """
        def existence(path, type_):
            if type_ == "dir":
                return os.path.isdir(path)
            elif type_ == "file":
                return os.path.isfile(path)

        def permission_access(path):
            return (os.access(path, os.R_OK) and os.access(path, os.W_OK))

        def create_json_file(path=path_json):
            with open(path, "w", encoding="utf-8") as f:
                f.write("[]")
                f.close()

        if existence(path_dir, "dir"):
            if not permission_access(path_dir):
                raise PermissionError("Directory permission denied.")
        else:
            os.mkdir(path_dir)
            create_json_file()

        if existence(path_json, "file"):
            if not permission_access(path_json):
                raise PermissionError("File permission denied.")
        else:
            create_json_file()
        return True

    def _terminal_width(self):
        """
        For practical reasons minimal terminal width should be >= 80px.
        """
        terminal_width = shutil.get_terminal_size().columns
        if not terminal_width >= 80:
            raise ValueError("Minimum terminal width is: 80px.")

    def _ansi_support(self):
        """
        https://en.wikipedia.org/wiki/ANSI_escape_code
        """
        term_emulator = os.getenv("TERM")
        return bool(term_emulator in self.term_list)


class Storage:
    """
    Class as a driver for read/write in the storage (json file).
    """
    def __init__(self, x, json_array=None, path=json_storage):
        self.x = x
        self.json_array = json_array
        self.path = path

        try:
            with open(self.path, self.x, encoding="utf-8") as file_:
                if self.x == "r":
                    self.json_array = json.load(file_)
                else:
                    json.dump(self.json_array, file_, indent=4)
                file_.close()
        except json.JSONDecodeError as exc:
            print(f"ERROR: {exc}")
            sys.exit(1)

    @property
    def output(self):
        return self.json_array


def object_enum(objects_list):
    """
    After deleting item in array, rearrange array indexes.
    """
    idx = 1
    enum_list = []
    for obj in objects_list:
        obj["idx"] = idx
        enum_list.append(obj)
        idx += 1
    return enum_list


class Group:
    """
    Group construction class.
    """
    def __init__(self, idx, name, tasks=[]):
        self._idx = idx
        self._name = name
        self._tasks = tasks

    @property
    def group(self):
        return {
            "idx": self._idx,
            "name": self._name,
            "tasks": self._tasks
        }

    @group.setter
    def group(self, task):
        self._tasks.append(task)


class Task:
    """
    Task construction class.
    """
    def __init__(self, idx, name, state, start, end, subtasks=[]):
        self._idx = idx
        self._name = name
        self._state = state
        self._start = start
        self._end = end
        self._subtasks = subtasks

    @property
    def task(self):
        return {
            "idx": self._idx,
            "name": self._name,
            "state": self._state,
            "start": self._start,
            "end": self._end,
            "subtasks": self._subtasks
        }

    def plus_subtask(self, subtask):
        # Adding subtasks.
        idx = len(self._subtasks) + 1
        self._subtasks.append({"idx": idx, "name": subtask, "check": False})


host = Host()  # Initialize detection for possible corruptions.
ansi_support = host.ansi_support  # Placeholder for ansi support.


# RETRIEVE GROUPS FROM JSON AND ASSIGN NEXT GROUP INDEX
groups = Storage("r").output
new_group_idx = len(groups) + 1


####################
# JSON MODIFICATIONS
####################
def create(group, task_name, opt_subtasks=False):
    """
    Create a new group, a new task and optionally subtasks.
    Or create a new task to the existing group and optionally subtasks.
    """
    # New group.
    if type(group) == str:
        new_task = Task(idx=1,
                        name=task_name,
                        state="pending",
                        start=current_date,
                        end=None,
                        subtasks=[])

        new_group = Group(idx=new_group_idx, name=group)
        new_group.group = new_task.task  # Add task to the group.
        groups.append(new_group.group)  # Add new group to the array.

    # Existing group.
    elif type(group) == int:
        selected_group = groups[group - 1]["tasks"]
        new_task = Task(idx=len(selected_group) + 1,
                        name=task_name,
                        state="pending",
                        start=current_date,
                        end=None,
                        subtasks=[])

        # Assign task to the group.
        selected_group.append(new_task.task)

    # Bad values, raise error.
    else:
        raise ValueError("Wrong input values.")

    # Optional subtasks.
    if opt_subtasks:
        for subtask in opt_subtasks:
            new_task.plus_subtask(subtask)


def change_group_name(group_idx, new_name):
    """
    Rename group without other modifications.
    """
    groups[group_idx - 1]["name"] = new_name


def delete_group_or_task(gidx, tidx=False):
    """
    Delete custom amount of group(s) or task(s).
    """
    if not tidx:
        idx_dec = 1
        if type(gidx) == int:
            del groups[gidx - 1]
        elif type(gidx) == list:
            for idx in sorted(gidx):
                del groups[idx - idx_dec]
                idx_dec += 1
        object_enum(groups)
    else:
        select_group = groups[gidx - 1]["tasks"]
        idx_dec = 1
        if type(tidx) == int:
            del select_group[tidx - 1]
        elif type(tidx) == list:
            for idx in sorted(tidx):
                del select_group[idx - idx_dec]
                idx_dec += 1
        object_enum(select_group)


def task_modificator(group_idx, task_idx, mod, value):
    """
    Functions for modifying task values.
    """
    selected_task = groups[group_idx - 1]["tasks"][task_idx - 1]

    def rename_task(task=selected_task, new_value=value):
        task["name"] = value

    def change_state(task=selected_task, new_value=value):
        """
        Change progress of the task to in-progres or done.
        Same value as before will revert to pending.
        """
        if new_value == selected_task["state"]:
            task["state"] = "pending"
            task["end"] = None
        elif new_value == "in-progress":
            task["state"] = "in-progress"
            task["end"] = None
        else:
            task["state"] = "done"
            task["end"] = current_date

    def add_subtask(task=selected_task, value_=value):
        """
        Add one or more subtasks.
        """
        for subtask_name in value_:
            new_idx = len(task["subtasks"]) + 1
            subtask_object = {
                "idx": new_idx, "name": subtask_name, "check": False
            }
            task["subtasks"].append(subtask_object)

    def delete_subtask(task=selected_task, idx_plus=value):
        """
        Delete one or more subtasks.
        """
        idx_dec = 1
        for idx in sorted(idx_plus):
            del task["subtasks"][idx - idx_dec]
            idx_dec += 1
        task["subtasks"] = object_enum(task["subtasks"])

    def rename_subtask(task=selected_task, idx_value=value):
        """
        Rename single subtask.
        """
        task["subtasks"][idx_value[0] - 1]["name"] = idx_value[1]

    # Call appropriate inner function.
    if mod == "name":
        rename_task()
    elif mod == "state":
        change_state()
    elif mod == "add_subtask":
        add_subtask()
    elif mod == "delete_subtask":
        delete_subtask()
    elif mod == "rename_subtask":
        rename_subtask()


def multi_task_progress(gidx, idx_list, value):
    """
    Multi-progress tasks settings.
    """
    for _ in range(len(idx_list)):
        task_modificator(gidx, idx_list[_], "state", value)


def task_mark(gidx, tidx):
    """
    Mark/unmark task as important.
    """
    task = groups[gidx - 1]["tasks"][tidx - 1]
    if task["name"][:4] == "[!] ":
        task["name"] = task["name"][4:]
    else:
        task["name"] = "[!] " + task["name"]


def tick_subtask(gidx, tidx, sidx_list):
    """
    Label subtask as done or revert back to previous state.
    """
    task = groups[gidx - 1]["tasks"][tidx - 1]
    if task["state"] == "done":
        print(
            "error: if parrent task is marked as done state of subtasks "
            "are locked, if you want to change state of subtasks you need "
            "to change parrent task state to 'pending' or 'in-progress'."
        )
        sys.exit(1)

    for st in sidx_list:
        try:
            subtask = task["subtasks"][st - 1]
            if subtask["check"]:
                subtask["check"] = False
            else:
                subtask["check"] = True
        except IndexError:
            pass


#######################
# TERMINAL PRESENTATION
#######################
class Cosmetics:
    """
    Class for terminal presentation cosmetics.
    """
    def __init__(self):
        self.ANSI = ansi_support
        self.term_width = shutil.get_terminal_size().columns
        self.dyn_part_len = self.term_width - 36 - 8

    def _max_str_length(self, string_array, type_):
        """
        If task or subtask can't fit in terminal cols, shrink it.
        """
        max_task = self.dyn_part_len - 1
        max_subtask = self.dyn_part_len - 5

        if type_ == "task":
            minus_len_task = max_task - len(string_array)
            if len(string_array) > max_task:
                return f" {string_array[:minus_len_task - 3]}..."
            return f" {string_array}"
        else:
            minus_len_subtask = max_subtask - len(string_array)
            if len(string_array) > max_subtask:
                return f" {string_array[:minus_len_subtask - 6]}..."
            return f" {string_array}"

    def _idx_format(self, idx):
        """
        If index is single digit then add one more space in front.
        """
        if idx > 9:
            return f"{idx} "
        return f" {idx} "

    def taskmeta(self, task):
        """
        Function for manipulating task properties and decoration.
        """
        sq = "█"
        pending = "☐"
        inprog = "…"
        done = "✔"

        # symbol
        idx_format = self._idx_format(task["idx"])
        if task["state"] == "pending":
            symbol = f" {pending} "
            task["name"] = f"☰ {task['name']}"
        elif task["state"] == "in-progress":
            symbol = f" {inprog} "
            task["name"] = f"⛶ {task['name']}"
        else:
            symbol = f" {done} "
            task["name"] = f"⦿ {task['name']}"

        # start/end
        start = f" {task['start']} "
        if task["end"] is None:
            end = f"{6 * ' '}⛌{6 * ' '}"
        else:
            end = f" {task['end']} "

        # name shrink/ansi
        if self.ANSI and (task["state"] == "done"):
            name = self._max_str_length(task["name"], "task")
            name_format = f"{name[:3]}\033[9m{name[3:]}\033[0m"
        else:
            name_format = self._max_str_length(task["name"], "task")
        compose_task = f"{idx_format}{sq}{symbol}{sq}{start}{sq}{end}{sq}"
        print(f"{4 * ' '}{compose_task + name_format}")

    def subtaskmeta(self, subtask, last=False):
        """
        Subtask cosmetics.
        """
        subtask_format = self._max_str_length(subtask["name"], "subtask")
        # print(f"_{subtask_format}_")
        if subtask["check"]:
            if self.ANSI:
                subtask_format = " ✔ " + f"\033[9m{subtask_format[1:]}\033[0m"
            else:
                subtask_format = " ✔ " + subtask_format[1:]
        else:
            subtask_format = " ☐ " + subtask_format[1:]

        pretty = f"{3 * '░'}█{3 * '░'}█{13 * '░'}█{13 * '░'}█"
        if not last:
            print(f"{4 * ' '}{pretty} ├──{subtask_format}")
        else:
            print(f"{4 * ' '}{pretty} └──{subtask_format}")

    def group_print(self, group):
        """
        Task group basic informations.
        """
        pending = 0
        inprog = 0
        done = 0

        idx = group["idx"]
        name = group["name"]

        for task in group["tasks"]:
            if task["state"] == "pending":
                pending += 1
            elif task["state"] == "in-progress":
                inprog += 1
            else:
                done += 1

        total = pending + inprog + done
        group_format = f"\n{4 * ' '}#{idx} {name} [{done}/{total}]"
        print(group_format)

    def headline(self):
        """
        Headline columns: first part is always fixed
        length, second depends on terminal size. If ansi is supported
        headline is color inverted.
        """
        fixed_part = f" id{9 * ' '}start{10 * ' '}end{6 * ' '}"
        side_spaces = (self.dyn_part_len - len("task")) // 2
        dynamic_part = f"{side_spaces * ' '}task{side_spaces * ' '}"
        if self.ANSI:
            print(f"{4 * ' '}\033[7m{fixed_part + dynamic_part}\033[0m")
        else:
            print(f"{4 * ' '}{fixed_part + dynamic_part}")

    def overall_statistics(self):
        """
        Sum of tasks progress.
        """
        def quot(x, y):
            # x=done, y=total
            quotient = x / y
            return round(quotient * 100)

        pending = 0
        inprog = 0
        done = 0

        for g in groups:
            tasks = g["tasks"]
            for t in tasks:
                if t["state"] == "pending":
                    pending += 1
                elif t["state"] == "in-progress":
                    inprog += 1
                else:
                    done += 1

        total = pending + inprog + done
        perc = quot(done, total)

        print(f"\n{4*' '}[{done}/{total}] - {perc}% of all tasks complete.")
        if self.ANSI:
            print(
                f"{4*' '}\033[4m[{done}] DONE\033[0m"
                f" • \033[4m[{inprog}] IN-PROGRESS\033[0m"
                f" • \033[4m[{pending}] PENDING\033[0m\n"
            )
        else:
            print(
                f"{4*' '}[{done}] DONE"
                f"• [{inprog}] IN-PROGRESS"
                f"• [{pending}] PENDING\n"
            )


def group_board(idx):
    """
    Single group board.
    """
    Cosmetics().group_print(groups[idx - 1])
    Cosmetics().headline()
    for task in groups[idx - 1]["tasks"]:
        Cosmetics().taskmeta(task)
        for subtask in task["subtasks"]:
            if subtask is task["subtasks"][-1]:
                Cosmetics().subtaskmeta(subtask, last=True)
            else:
                Cosmetics().subtaskmeta(subtask)


def show_task(gidx, tidx):
    """
    Expanded task view.
    """
    group = groups[gidx - 1]
    task = group["tasks"][tidx - 1]
    print(task["name"])


def show_subtask(gidx, tidx, sidx):
    """
    Expanded subtask view.
    """
    group = groups[gidx - 1]
    task = group["tasks"][tidx - 1]
    subtask = task["subtasks"][sidx - 1]
    print(subtask["name"])


def board(arg=False):
    """
    If arg True show board with subtasks, else without.
    """
    if len(groups) == 0:
        print("No tasks assigned, create one with 'add --new' commands.")

    for group in groups:
        Cosmetics().group_print(group)
        Cosmetics().headline()
        for task in group["tasks"]:
            Cosmetics().taskmeta(task)

            if arg:
                for subtask in task["subtasks"]:
                    if subtask is task["subtasks"][-1]:
                        Cosmetics().subtaskmeta(subtask, last=True)
                    else:
                        Cosmetics().subtaskmeta(subtask)

    if len(groups) > 0:
        Cosmetics().overall_statistics()


def list_subtasks(gidx, tidx):
    """
    List numerated subtasks.
    """
    subtasks_list = ""
    subtasks = groups[gidx - 1]["tasks"][tidx - 1]["subtasks"]
    if len(subtasks) == 0:
        print("No subtasks assigned to the task.")
        return
    for subtask in subtasks:
        subtasks_list += f"{subtask['idx']}. {subtask['name']}\n\t"
    subtasks_print = f"""
        {subtasks_list}"""
    print(subtasks_print)


####################
# PARSER / SUBPARSER
####################
parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest="command")
parser.add_argument(
    "-b", "--board", action="store_true", help="show board with subtasks"
)
parser.add_argument(
    "-r", "--reset", action="store_true", help="reset tasks board"
)
parser.add_argument(
    "--mark", type=int, action="store", nargs=2,
    help="mark/unmark task as important", metavar="<idx>"
)
parser.add_argument(
    "--show", type=int, action="store", nargs="+",
    help="show group or task or subtask", metavar="<idx>"
)
parser.add_argument(
    "--tick", type=int, action="store", nargs="+",
    help="tick/untick subtask(s) as done", metavar="<idx>"
)
parser.add_argument(
    "--ls-sub", type=int, action="store", nargs=2,
    help="list numerated subtasks", metavar="<idx>"
)

#####
# ADD
#####
add = subparser.add_parser("add", help="create group/task or assign task")
add.add_argument(
    "-g", "--group", type=int, action="store", nargs=1, metavar="<idx>",
    help="select group (in conjunction with --assign)"
)
add_opt = add.add_mutually_exclusive_group(required=True)
add_opt.add_argument(
    "--new", type=str, action="store", nargs="*", help="create new group/task",
    metavar="<str>"
)
add_opt.add_argument(
    "--assign", type=str, action="store", nargs="+",
    help="assign task to the group", metavar="<str>"
)

########
# RENAME
########
rename = subparser.add_parser("rename", help="rename group or task")
rename.add_argument(
    "-g", "--group", action="store", nargs="*", metavar="<idx>",
    help="rename single group", required=True
)
rename.add_argument(
    "-t", "--task", action="store", nargs=2, metavar="<idx>",
    help="rename single task"
)

########
# DELETE
########
delete = subparser.add_parser("delete", help="delete group(s) or task(s)")
delete.add_argument(
    "-g", "--group", type=int, action="store", nargs="+", metavar="<idx>",
    help="delete single/multiple groups", required=True
)
delete.add_argument(
    "-t", "--task", type=int, action="store", nargs="+", metavar="<idx>",
    help="delete single/multiple tasks"
)

##############
# SET PROGRESS
##############
progress = subparser.add_parser(
    "set", help="set task(s) progress to in-progress/done"
)
progress.add_argument(
    "-g", "--group", type=int, action="store", nargs=1, required=True,
    metavar="<idx>", help="select group"
)
progress_opt = progress.add_mutually_exclusive_group(required=True)
progress_opt.add_argument(
    "--done", type=int, action="store", nargs="+", metavar="<idx>",
    help="change task(s) progress to done"
)
progress_opt.add_argument(
    "--inprog", type=int, action="store", nargs="+", metavar="<idx>",
    help="change task(s) progress to in-progress"
)

#################
# MODIFY SUBTASKS
#################
sub = subparser.add_parser(
    "sub", help="add/rename/delete subtask(s)"
)
sub.add_argument(
    "--idx", type=int, action="store", nargs="*", metavar="<idx>",
    help="select group idx - task idx - subtask idx", required=True
)
sub_opt = sub.add_mutually_exclusive_group(required=True)
sub_opt.add_argument(
    "--add", type=str, action="store", nargs="+", metavar="<str>",
    help="add subtask(s)"
)
sub_opt.add_argument(
    "--rename", type=str, action="store", nargs=1, metavar="<str>",
    help="rename subtask"
)
sub_opt.add_argument(
    "--delete", type=int, action="store", nargs="+", metavar="<idx>",
    help="delete subtask(s)"
)
args = parser.parse_args()


################
# MAIN EXECUTION
################
def limit_cli_options():
    """
    Limit to only one command per cli execution.
    """
    user_input = 0
    commands = vars(args).items()
    for command in commands:
        if command[1]:
            user_input += 1
        if command[0] == "ls_sub":
            break
    if user_input > 1:
        raise SyntaxError("error: only one command allowed per exection.")


def args_policy(cmd=args.command):
    """
    Raise errors on invalid arg syntax.
    """
    for arg in vars(args):
        # Check if there is user input with negative integer or zero.
        current_arg = eval(f"args.{arg}")
        if type(current_arg) == list:
            for value in current_arg:
                if type(value) == int:
                    if value <= 0:
                        raise ValueError(
                            "error: args must be positive and gt than zero."
                        )

    if args.tick:
        # User input must be at least 3 integers
        if not len(args.tick) >= 3:
            raise ValueError(
                "error: --tick: option requires at least three args."
            )

    if cmd == "add":
        if args.new == []:
            raise ValueError("error: --new: minimum two arg values.")
        if args.new:
            if len(args.new) < 2:
                raise ValueError("error: --new: minimum two arg values.")
            if args.group:
                raise SyntaxError(
                    "error: -g/--group: can't be used with --new."
                )
        if args.assign:
            if not args.group:
                raise SyntaxError(
                    "error: --assign: "
                    "should be used in conjunction with -g/--group."
                )

    elif cmd == "rename":
        if args.group == []:
            raise SyntaxError("error: -g/--group: provide at least one arg.")
        try:
            args.group[0] = int(args.group[0])
        except ValueError:
            raise ValueError(
                "error: -g/--group: value should be integer."
            )

        if args.task:
            try:
                args.task[0] = int(args.task[0])
            except ValueError:
                pass
            if len(args.group) > 1:
                raise ValueError(
                    "error: -g/--group: only one arg value required, "
                    "in conjunction with -t/--task."
                )
            elif type(args.task[0]) is not int:
                raise ValueError(
                    "error: -t/--task: first value should be integer."
                )
            else:
                if type(args.group[0]) is not int:
                    raise ValueError(
                        "error: -g/--group: value should be integer."
                    )
        else:
            if len(args.group) != 2:
                raise ValueError(
                    "error: -g/--group: two arg values required when "
                    "used without -t/--task command."
                )

    elif cmd == "delete":
        if args.task:
            if len(args.group) > 1:
                raise ValueError(
                    "error: -g/--group: only one arg value required, "
                    "in conjunction with -t/--task."
                )

    elif cmd == "sub":
        if args.idx == []:
            raise ValueError("error: --idx: two or three values required.")

        if args.add or args.delete:
            if not len(args.idx) == 2:
                raise ValueError(
                    "error: --idx: in conjunction with --add/--delete: "
                    "two arg values required."
                )
        else:
            if not len(args.idx) == 3:
                raise ValueError(
                    "error: --idx: in conjuntion with --rename: "
                    "three arg values required."
                )


def confirm():
    """
    For destructive operations, ask user to confirm.
    """
    choice = input("Do you want to proceed [y/N]: ")
    if choice.lower() == "y":
        return True
    else:
        print("aborted.")
        sys.exit(1)


def main():
    """
    Run program.
    """
    if args.board:
        board(arg=True)

    if args.reset:
        print("Executing restart command...")
        confirm()
        Storage("w", [])

    if args.show:
        if len(args.show) == 1:
            group_board(args.show[0])
        elif len(args.show) == 2:
            show_task(args.show[0], args.show[1])
        else:
            show_subtask(args.show[0], args.show[1], args.show[2])

    if args.mark:
        task_mark(args.mark[0], args.mark[1])
        Storage("w", groups)  # Save changes.

    if args.tick:
        tick_subtask(args.tick[0], args.tick[1], args.tick[2:])
        Storage("w", groups)  # Save changes.

    if args.ls_sub:
        list_subtasks(args.ls_sub[0], args.ls_sub[1])

    if args.command:
        if args.command == "add":
            if args.new:
                if len(args.new) == 2:
                    create(args.new[0], args.new[1])
                else:
                    create(args.new[0], args.new[1], args.new[2:])
            else:
                if len(args.assign) == 1:
                    create(args.group[0], args.assign[0])
                else:
                    create(args.group[0], args.assign[0], args.assign[1:])

        elif args.command == "rename":
            if args.group and args.task:
                task_modificator(
                    args.group[0], args.task[0], "name", args.task[1]
                )
            else:
                change_group_name(args.group[0], args.group[1])

        elif args.command == "delete":
            print("You are about to delete objective(s)...")
            confirm()
            if args.task:
                delete_group_or_task(args.group[0], list(set(args.task)))
            else:
                delete_group_or_task(list(set(args.group)))

        elif args.command == "set":
            if args.done:
                multi_task_progress(args.group[0], args.done, "done")
            else:
                multi_task_progress(args.group[0], args.inprog, "in-progress")

        elif args.command == "sub":
            if args.add:
                task_modificator(
                    args.idx[0], args.idx[1], "add_subtask", args.add
                )
            elif args.rename:
                task_modificator(
                    args.idx[0], args.idx[1], "rename_subtask",
                    [args.idx[2], args.rename[0]]
                )
            else:
                task_modificator(
                    args.idx[0], args.idx[1], "delete_subtask", args.delete
                )

        # Save changes.
        Storage("w", groups)

    if args.board == args.reset:
        if args.command == args.mark == args.show == args.tick == args.ls_sub:
            board()


if __name__ == "__main__":
    try:
        limit_cli_options()
        args_policy()
        main()
    except IndexError:
        print("error: index out of range")
    except SyntaxError as exc:
        print(exc)
    except ValueError as exc:
        print(exc)
