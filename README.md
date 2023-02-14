# DCoMEX Tools
A set of tools for preprocessing of data for the DCoMEX project

## Dependencies
1. Python3.
2. pyenv module for management of virtual environments. This can be installed with the tool itself if you don't already have it (see [Initialization of the application](#initialization-of-the-application)). 
3. Linux Based OS (Well tested on Ubuntu but should work on MacOs and other linux systems)
4. Note!!: Does not work on windows at the moment!


## Installation
1. Install with pip through `pip install git+https://github.com/giesekow/dcomex-tools.git`


## Getting started
After installation the cli can be accessed on the terminal using `dcomex`  
Run `dcomex --help` to get the help message.
```
usage: dcomex [-h] {gui,init,plugin,run} ...

A Command line tool for the dicomex processing tool

positional arguments:
  {gui,init,plugin,run}

optional arguments:
  -h, --help            show this help message and exit
```
The tool has submodules that can be accessed for management of the graphical User Interface (GUI), Plugins, Processing, etc.

## Initialization of the application
Before you use the tool for any processing make sure you run the initialization code below. This needs to be executed only once after the installation and not every time.  
`dcomex init`
```
usage: dcomex init [-h] [-r]

Initialize the app

optional arguments:
  -h, --help            show this help message and exit
  -r, --install-requirements
                        Install requirements in the process [pyenv]
```
* You can add the `-r` switch to install other requirements (pyenv, ants, etc.) if you don't already have it installed.
* The initialization process might take some time to complete and it installs the default plugins into the working space
* The default plugins include the follow:  
  1. brat_preprocessor
  2. brat_tissue
  3. brat_segmentation
  4. volume2mesh
  5. itksnap (viewer)
  6. paraview (viewer)
  7. gmsh (viewer)


## The graphical User Interface
The tool comes with a user interface that can be used to manage plugins and process data. To access the GUI run the code below:  
`dcomex gui`  
NOTE:  
To use the gui you need to install `pyQt5`.

## Plugin Management
The tool works with custom plugins and these plugins can be managed using the `plugin` submodule. To get a list of available options type the command below on the terminal  
`dcomex plugin --help`

```
usage: dcomex plugin [-h] {create,install,remove,list,info,set} ...

Manage the plugin sub module

positional arguments:
  {create,install,remove,list,info,set}

optional arguments:
  -h, --help            show this help message and exit
```

### Create a plugin template
Plugin have specific format and structure. To create a plugin template use the command below:  
`dcomex plugin create`
```
usage: dcomex plugin create [-h] type path

Create a template with the required structure for a plugin

positional arguments:
  type        The template type to be created [executable, python]
  path        The path to the template to be created!

optional arguments:
  -h, --help  show this help message and exit
```
Once you have the template created you can fill in with actual information and code and then install it in the step below.

### Install a plugin
Before a plugin can be used it needs to be installed first. To install a plugin execute the command below:  
`dcomex plugin install`
```
usage: dcomex plugin install [-h] [-s SETTINGS] [-t TYPE] [-g GROUP] [-n DISPLAY] [--git] [--viewer] name path

Install a plugin

positional arguments:
  name                  The unique name to the plugin
  path                  The path to the plugin, this can be a local folder or a git repo

optional arguments:
  -h, --help            show this help message and exit
  -s SETTINGS, --settings SETTINGS
                        The path to the settings json file relative to the plugin path. Default to "settings.json"
  -t TYPE, --type TYPE  The type of the plugin. Defaults to "python"
  -g GROUP, --group GROUP
                        The group to install the plugin to. Defaults to None
  -n DISPLAY, --display DISPLAY
                        Plugin display name. Defaults to unique name
  --git                 Installation path is a git repo
  --viewer              Installation path is a git repo
```
Once a plugin is installed it can be invoked using the `run` sub-command which will be discussed in the processing section.

### Remove an existing plugin
To remove an already installed plugin run the command below:  
`dcomex plugin remove`
```
usage: dcomex plugin remove [-h] [-y] [name [name ...]]

Remove a plugin

positional arguments:
  name        The names of plugins to be removed

optional arguments:
  -h, --help  show this help message and exit
  -y          Answer yes to all questions
```

### List existing plugins
To show a list of existing plugins execute the command below:  
`dcomex plugin list`
```
usage: dcomex plugin list [-h]

List installed plugins

optional arguments:
  -h, --help  show this help message and exit
```

### Show detailed information about a plugin
To show detailed information about a particular plugin execute the command below:  
`dcomex plugin info`
```
usage: dcomex plugin info [-h] plugin_name

Show detailed information about a specific installed plugins

positional arguments:
  plugin_name  The plugin to display the information for

optional arguments:
  -h, --help   show this help message and exit
```


### Modify plugin information
The information about an existing plugin can be modified using the command below:  
`dcomex plugin set`
```
usage: dcomex plugin set [-h] [-k KWARGS] plugin_name

Update information about an existing plugin

positional arguments:
  plugin_name           The plugin to update the information for

optional arguments:
  -h, --help            show this help message and exit
  -k KWARGS, --kwarg KWARGS
                        Named set arguments for the plugin in yaml or json format
```

## Processing data with installed plugins
Installed plugins can be executed using the command below:  
`dcomex run`
```
usage: dcomex run [-h] [-i INPUTS] [-o OUTPUTS] [-p PREFIX] [--input-file INPUT_FILE] [--output-file OUTPUT_FILE] [--pipe PIPE] [--forward-outputs] plugin_name

Invoke the processing engine

positional arguments:
  plugin_name           The plugin to invoke

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTS, --input INPUTS
                        named input arguments for the plugin in yaml or json format
  -o OUTPUTS, --output OUTPUTS
                        output mapping in yaml or json format, useful for piping plugins
  -p PREFIX, --prefix PREFIX
                        prefix for outputs from the plugin, defaults to empty string
  --input-file INPUT_FILE
                        Path to a json file containing input information
  --output-file OUTPUT_FILE
                        Path to a json file to store the output information
  --pipe PIPE           pipe another run command, a string which takes all the existing options
  --forward-outputs     Forward previous outputs to piped plugin
```
* `INPUTS` are `key:value` arguments which are required by the plugin that is being invoked. To know what arguments are required you can check the plugin's settings through `dcomex plugin info [plugin-name]`.
* `OUTPUTS` are `key:value` arguments that maps output from the plugin to a different name. This can be useful which running a pipeline of multiple plugins and output from one plugin needs to be renamed to serve as input to another plugin.

## Running a pipeline of multiple plugins
Multiple plugins can be channelled together to form a pipeline to do this use the `--pipe PIPE` option to the `dcomex run` command. The `PIPE` value is then a new set of `run` command which takes all the arguments of the original `run` command including `--pipe` itself. The `PIPE` might therefore need appropriate quoting.  

* For example you can process an image and open the output with a viewer with a pipeline command:  
  *  Assuming image processing plugin output file with name same as the imput name to the viewer.  
`dcomex run [process-plugin] -i input_file:[path] --pipe [viewer-plugin]`
  * Where output from image processing has a different name compared to input to viewer, we can map the output from image process to the input of the viewer using the `-o` argument.  
  `dcome run [process-plugin] -i input_file:[path] -o [viewer_input]:[process_output] --pipe [viewer-plugin]`


# Default Plugins
This section discusses the default plugins which are available through the `init` command. If you have not already initialize the tool then have a look at the [initialization section](#initialization-of-the-application).

## BRAT Preprocessing Plugin
This plugin takes as input t1, t1c, t2, fla images and outputs same modalities which have been co-registered and skullstripped.  

The plugin can be executed using the command below:  
```
dcomex run brat_preprocessor -i t1:[t1-path] -i t1c:[t1c-path] -i t2:[t2-path] -i fla:[fla-path] -i outputDir:[output-dir]
```

where:  
* `[t1-path]`: is the path to the t1 nifti file.
* `[t1c-path]`: is the path to the t1c nifti file.
* `[t2-path]`: is the path to the t2 nifti file.
* `[fla-path]`: is the path to the flair nifti file.
* `[output-dir]`: is path to a directory where output files will be saved.

You can execute `dcomex run --help` to view other available arguments to the `run` command.

## BRAT Segmentation (Tumor segmentation)
This plugin takes as input t1, t1c, t2, fla images and outputs the tumor segmentation.  

The plugin can be executed using the command below:  
```
dcomex run brat_segmentation -i t1:[t1-path] -i t1c:[t1c-path] -i t2:[t2-path] -i fla:[fla-path] -i outputDir:[output-dir]
```

where:  
* `[t1-path]`: is the path to the t1 nifti file.
* `[t1c-path]`: is the path to the t1c nifti file.
* `[t2-path]`: is the path to the t2 nifti file.
* `[fla-path]`: is the path to the flair nifti file.
* `[output-dir]`: is path to a directory where output files will be saved.

You can execute `dcomex run --help` to view other available arguments to the `run` command.


## BRAT Tissue (Tissue segmentation)
This plugin takes as input t1, image and outputs the tissue (wm, gm, csf) probabilities and class segmentation.  

The plugin can be executed using the command below:  
```
dcomex run brat_tissue -i t1:[t1-path] -i threshold:[prob-threshold] -i outputDir:[output-dir]
```

where:  
* `[t1-path]`: is the path to the t1 nifti file.
* `[prob-threshold]`: is the value used to threshold the probabilities to obtain the bins and defaults to 0.5.
* `[output-dir]`: is path to a directory where output files will be saved.

You can execute `dcomex run --help` to view other available arguments to the `run` command.


## Volume to Mesh
This plugin takes a mask and features in nifti format and create a volumetric mesh from it.  

The plugin can be executed using the command below:  
```
dcomex run volume2mesh -i mask:[mask-path] -i features:[feature-path-list] -i zoom_value:[zoom] -i r_start:[mask-min-value] -i r_end:[mask-max-value] -i outputDir:[output-dir]
```

where:  
* `[mask-path]`: is the path to the mask nifti file.
* `[feature-path-list]`: a list of file paths containing nifti image with features. This should be a json list.
* `[zoom]`: a zooming factor applied to images before meshing defaults to 1 which applies not zoom.
* `[mask-min-value]`: minimum value to consider within the provided mask.
* `[mask-max-value]`: maximum value to consider within the provided mask.
* `[output-dir]`: is path to a directory where output files will be saved.

You can execute `dcomex run --help` to view other available arguments to the `run` command.

## Viewers
The following viewers are available through the initialization:
* itksnap
* paraview
* gmsh

They can be executed as 
```
dcomex run [viewer-name] -i data:[file-path]
```
where:  
* `[viewer-name]`: is one of the viewers above.
* `[file-path]`: is the file to be open in the viewer. This is optional and will open a blank viewer if not provided.
* `itksnap` takes additional `-i seg:[seg-file-path]` argument which can be used to load a segmentation file.
