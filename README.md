# arcflow
Single file program that works with python standard library. It's nice to pair with drop-down terminal like yakuake. Main purpose is to keep short-term task objectives terminal accessible, perfect for your project design guidelines and similar stuff.

## install
```
# clone repo
git clone https://github.com/pbunic/arcflow.git <dir_path>

# copy arcflow
cd <dir_path>
sudo cp -p arcflow.py /usr/local/bin/arcflow
```

## uninstall
```
# remove arcflow
sudo rm /usr/local/bin/arcflow

# if you don't need json file anymore
rm -r ~/.arcflow
```

## screenshots
![screenshot](/img/img1.png)

![screenshot -b](/img/img2.png)

## help
```
usage: arcflow [-h] [-b] [-r] [--mark <idx> <idx>] [--show <idx> [<idx> ...]] [--tick <idx> [<idx> ...]]
               [--ls-sub <idx> <idx>]
               {add,rename,delete,set,sub} ...

positional arguments:
  {add,rename,delete,set,sub}
    add                 create group/task or assign task
    rename              rename group or task
    delete              delete group(s) or task(s)
    set                 set task(s) progress to in-progress/done
    sub                 add/rename/delete subtask(s)

options:
  -h, --help            show this help message and exit
  -b, --board           show board with subtasks
  -r, --reset           reset tasks board
  --mark <idx> <idx>    mark/unmark task as important
  --show <idx> [<idx> ...]
                        show group or task or subtask
  --tick <idx> [<idx> ...]
                        tick/untick subtask(s) as done
  --ls-sub <idx> <idx>  list numerated subtasks
```

## usage examples
```
# arcflow without options shows tasks (subtasks are hidden).
# arcflow with -b argument shows with subtasks:
arcflow -b


# you can reset json file with -r flag
arcflow -r


# you can mark task as important or remove mark
arcflow --mark <group_index> <task_index>


# single group shown (with group/tasks/subtasks)
arcflow --show <group_index>

# single task shown (if task can't fit in terminal width)
arcflow --show <group_index> <task_index>

# single subtask show (if subtask can't fit in terminal width)
arcflow --show <group_index> <task_index> <subtask_index>

# you can print subtask indexes with
arcflow --ls-sub <group_index> <task_index>

# you can tick/check subtask(s) as done or untick/uncheck
arcflow --tick <group_index> <task_index> [<subtask_index> ...]


# ADD
# create new group/task/subtasks
arcflow add --new <group> <task> [<subtask> ...]

# create new task/subtasks for existing group
arcflow add -g <group_index> --assign <task> [<subtask> ...]


# RENAME
# rename group
arcflow rename -g <group_index> <new_group_name>

# rename task
arcflow rename -g <group_index> -t <task_index> <new_task_name>


# DELETE
# you can delete one or more groups
arcflow delete -g <group_index> ...

# you can delete one or more tasks in the group
arcflow delete -g <group_index> -t <task_index> ...


# SET
# set task progress to "in-progress" (in the single group)
arcflow set -g <group_index> --inprog <task_index> ...

# set task progress to "done" (in the single group)
arcflow set -g <group_index> --done <task_index> ...


# SUB
# add subtask(s)
arcflow sub --idx <group_index> <task_index> --add [<subtask_name> ...]

# rename single subtask
arcflow sub --idx <group_index> <task_index> <subtask_index> --rename <new_subtask_name>

# delete subtask(s)
arcflow sub --idx <group_index> <task_index --delete [<subtask_index> ...]
```

## license
GNU General Public License v3.0
