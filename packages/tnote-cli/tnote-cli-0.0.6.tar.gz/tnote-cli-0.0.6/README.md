# tnote-cli
A simple notes Command line tool, because I really got tired of either:

A. going from the terminal into another app to write something down for later
or 
B. Forgetting which configuration file is where and not having a convenient place where all my notes could be kept

Plus I really just wanted a project to work on.

## Installation 

```
pip install tnote-cli
```


## Usage 

Using tnote is pretty simple when it really comes down to it as there is only one command that has several options. 


#### Index

The index of all the notes you've created can be accessed by `$ tnote` with no arguments.
At any point you can use `$ tn` as it is the same because who has time for all those extra keystrokes.

```
$ tnote 
|-------------------------INDEX-------------------------|


|-------------------------RECENT------------------------|
 Note ID: todo
 Name: todo.md
 Path: /Users/username/.tnote/notes/todo.md
|-------------------------------------------------------|
    
            _________________________________
            

|-------------------------------------------------------|
 Note ID: todo
 Name: todo.md
 Path: /Users/username/.tnote/notes/todo.md
|-------------------------------------------------------|

```
At first your index obviously won't look like this but create a note and you'll be good.
Up at the top there it will show you want is your most recently edited note which can be accessed 
using the `$ -r` flag.

#### Creating and Editing Notes

To create a new note you need only type in a name for a note like so `$ tn EXAMPLE` and a note will be created and 
you'll begin editing it. You can also specify editing with the `$ -e` flag. The editor used will be the `$EDITOR` 
environment variable but it can also be changed in the config at `~/.tnote.json`

```
$ tnote -e Example
```

```
$ tn Example
```

#### View

Tnote was designed with using markdown in mind as it is how I frequently take notes as 
such if you wish to render it from your terminal use the view flag.
```
$ tnote -v Example
```

#### Moving and Renaming
If you wish to rename a file simply do so by passing the same path other than the filename to the move option:
```
$ tnote Example -m ~/tnote/notes/new_name.md 
```
otherwise just pass a fully qualified path with filename to move the file:
```
$ tnote Example -m ~/Example.md
```


#### Delete
To permenantly delete a note:
```
$ tnote -d Example
```


#### Change ID
IF you want to change the Id you use to access notes you do so as shown below 
``` 
$ tnote Example -i new-id
```
to access this note in the future you'll use `new-id`

#### Execute 

From time to time I like to have some simple scripts on-hand for quick access 
so I have allowed a way to simply execute from my notes 

Execute a file that has permissions:
```
tnote Script -x
```

Give a file permission (chmod) and execute it:
```
tnote Script -xx
```


