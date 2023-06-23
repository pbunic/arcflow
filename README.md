# arcflow
will be updated.

## install
```
# clone repo
git clone https://github.com/pbunic/arcflow.git <DIR_NAME>

# copy arcflow
cd <DIR_NAME>
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
will be updated.

## about
will be updated.

## license
GNU General Public License v3.0
