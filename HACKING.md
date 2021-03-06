> Developer guide to the codebase, plus some design notes and philosophy

## Contents

- ['Functional core, imperative shell' + MVA?](#functional-core-imperative-shell--mva)
- [Cache directory structure](#cache-directory-structure)
- [UML diagrams](#uml-diagrams)
    - [Flowchart of modes and their connections](#flowchart-of-modes-and-their-connections)
    - [Simplified UML diagram of the classes](#simplified-uml-diagram-of-the-classes)
        - [api.py](#apipy)
        - [download.py](#downloadpy)
        - [Image Adjuster in assistants.py](#image-adjuster-in-assistantspy)
        - [lscat.py and data.py](#lscatpy-and-datapy)
        - [main.py to prompt.py](#mainpy-to-promptpy)
        - [main.py to ui.py](#mainpy-to-uipy)
        - [ui.py](#uipy)
        - [UI class methods](#ui-class-methods)
    - [Actor-ish models of ui classes](#actor-ish-models-of-ui-classes)
        - [ui.AbstractUI](#uiabstractui)
        - [ui.Gallery classes (extending AbstractUI)](#uigallery-classes-extending-abstractui)
        - [ui.User classes (extending AbstractUI)](#uiuser-classes-extending-abstractui)
        - [ui.Image](#uiimage)
- [Dependencies](#dependencies)
- [Internal imports](#internal-imports)

## 'Functional core, imperative shell' + MVA?

> "There are two roles of code: code that does work, and code that coordinates work" ([Sonmez](https://simpleprogrammer.com/there-are-only-two-roles-of-code/))

If there is one sentence to keep in mind while reading the code, this is it.

Although it seems contradictory, I think the code has uses both the functional-core-imperative-shell and the [model-view-adapter](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93adapter) OOP patterns.
* The models are the functional core.
* The views accepts user input (inbound IO) and interacts with the user (outbound IO) -- this is the imperative shell.
* The adapters mediates between the functional core and the imperative shell. They launches the views, get user input, calls the appropriate models, and send that to the appropriate views. 

In other words, the adapter organises code, while the models and view does the actual work.

<table>
<thead>
  <tr>
    <th>Role of code</th>
    <th>Model (functional core)</th>
    <th>Inbound IO (imperative shell)</th>
    <th>Outbound IO (imperative shell)<br></th>
    <th>Adapter (organizes everything)</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Does work</td>
    <td><ul>
        <li>colors</li>
        <li>config *</li>
        <li>data</li>
        <li>pure</li>
    </ul></td>
    <td><ul>
        <li>api</li>
        <li>config *</li>
        <li>download</li>
        <li>files</li>
        <li>utils *</li>
    </ul></td>
    <td><ul>
        <li>config *</li>
        <li>picker †</li>
        <li>printer</li>
        <li>screens</li>
        <li>utils</li>
    </ul></td>
    <td></td>
  </tr>
  <tr>
    <td>Organizes work</td>
    <td></td>
    <td><ul>
        <li>assistants †</li>
        <li>prompt †</li>
    </ul></td>
    <td><ul>
        <li>lscat</li>
    </ul></td>
    <td><ul>
        <li>cli</li>
        <li>lscat_app</li>
        <li>main</li>
        <li>ui</li>
    </ul></td>
  </tr>
</tbody>
</table>

The overall code is neither OOP nor functional: the only communication between all modules is through function returns, not through 'notifying' different objects. The only (major?) exception is that `downloads.py` will directly trigger a callback to `lscat.py`.

Now, this paints a rosy picture but in reality, there was no initial planning so the code was originally not written towards any structure or pattern. What still needs work is:
* The config contains a functional core, inbound IO, and outbound IO.
* †: technically both inbound and outbound, but main purpose is to provide a view for the user and catch user input

Here are some good tips:
* "The way to figure out the separation is by doing as much as you can without mutation, and then encapsulating the mutation separately" (Gary Bernhardt)
* "Create your application to work without either a UI or a database so you can run automated regression-tests against the application, work when the database becomes unavailable, and **link applications together without any user involvement**" ([Alistair Cockburn](https://github.com/jschairb/sandbox/wiki/HexagonalArchitecture)) (Emphasis mine)

It is possible to adapt koneko to work with sites other than pixiv:
    * At the very least, only the `api` and `data` modules need to be replaced.
    * The config already handles username and passwords, but you can add something like an API key or OTP auth
    * The navigation routes (eg pages, prompt handling) are in `ui.py`, while the starting dispatch logic is in `main.py`
    * See the [koneko-twitter](https://github.com/twenty5151/koneko-twitter) and [koneko-gelbooru](https://github.com/twenty5151/koneko-gelbooru/) repos for some rough examples


## Cache directory structure

```sh
$ cd ~/.local/share/koneko
$ tree -d  # (Edited: .koneko and history are files not directories)
.
├── cache                         # ├── KONEKODIR
│   ├── 2232374                   # │   ├── Artist pixiv ID                             ├── Mode 1 and 2
│   │   ├── 1                     # │   │   ├── Page 1                                  │   ├── Mode 1
│   │   ├── 2                     # │   │   ├── Page 2                                  │   ├── Mode 1
│   │   └── individual            # │   │   └── Posts with a single image               │   └── Mode 2
│   │       └── 76695217          # │   │       └── ID of posts with multiple images    │       ├── Mode 2
│   │           └── illustrelated # │   │       └── Related images mode                 │       └── Mode 1.5
│   │               └── 1         # │   │           └── Page 1                          │           └── Mode 1.5

│   ├── following                 # │   ├── Following users mode                        ├── Mode 3
│   │   └── *your_id*             # │   │   └── Your pixiv ID                           │
│   │       ├── 1                 # │   │       ├── Page 1                              │
│   │       │   └── .koneko       # │   │       │   └── Stores number of artists info   │
│   │       └── 2                 # │   │       └── Page 2                              │
│   │           └── .koneko       # │   │           └── Stores number of artists info   │

│   ├── illustfollow              # │   ├── Illust follow mode                          ├── Mode 5
│   │   ├── 1                     # │   │   ├── Page 1                                  │
│   │   └── 2                     # │   │   └── Page 2                                  │

│   ├── recommended               # │   ├── Illust recommended mode                     ├── Mode 6
│   │   └── 1                     # │   │   └── Page 1

│   ├── search                    # │   ├── Search users mode                           ├── Mode 4
│   │   └── gomzi                 # │   │   └── Search string
│   │       └── 1                 # │   │       └── Page 1

│   ├── history                   # │   ├── History file, for frequent "mode"

│   ├── testgallery               # │   ├── (Internal/debugging use)
│   └── testuser                  # │   └── (Internal/debugging use)
└── pics                          # └── Images for main and info screen
```


## UML diagrams

### Flowchart of modes and their connections

![Flowchart UML](puml/render/flowchart.png)


### Flowchart as a finite state machine

![api UML](puml/classes/render/state_flowchart.png)


### Simplified UML diagram of the classes

#### api.py

![api UML](puml/classes/render/api.png)

#### download.py

![download UML](puml/classes/render/download.png)

#### Image Adjuster in assistants.py

![image adjuster UML](puml/classes/render/image_adjuster.png)

#### lscat.py and data.py

![lscat and data UML](puml/classes/render/lscat_and_data.png)

#### main.py to prompt.py

![main to prompt UML](puml/classes/render/main_to_prompt.png)

#### main.py to ui.py

![main to ui UML](puml/classes/render/main_to_ui.png)


#### ui.py

![ui UML](puml/classes/render/ui.png)


#### UI class methods

![ui methods UML](puml/classes/render/ui_methods.png)



### Actor-ish models of ui classes
#### ui.AbstractUI
  
![AbstractUI UML](puml/actors/render/abstractui.png)
  
#### ui.Gallery classes (extending AbstractUI)

![Gallery UML](http://plantuml.com:80/plantuml/png/RL71QiCm3BthAtHCA3liq4iWeuD2Fw1iLwFL9dWuLh0LIY0VFzjnM3TwilJq93q_dQ9Ga7bq85QSmGivPyA28siJiSaFlY9vZSSMW6x20J-Y2G1zZv_MtD6ED1Xi1aRXckIk5liUCXDVtd2sU3Xq3tn8IC87JKAbD74KzHtPGp0o1_y0PCuNHOCsHt0BXcHFjZ4bxl2Qn2NHlvrRDOley6pZv6Y9V_Phldl7f8k4yvuKHXFRAcLNL60r1HudQLfOrnMA2nV6PA6DKlvTFJiYUxSyCs5WjT5L9gP1_wserJcrAQltxS_HzuBMessIJiRhV4-07m00)


#### ui.User classes (extending AbstractUI)
  
![User UML](http://plantuml.com:80/plantuml/png/TOun2iCm40JxUyMMDYPLKWKKdCelI2q4Ee90jk1qAW9wl2KbRTgPMTWrgnCjUoGD6Xclp98nxSaphaY2sqn4nc1BQ678Yk6CePxYya09M9Oxtib-0zk3QQR6c_LEtV0_MThA1a_2MkJuGv-3RYv6bW_LMjk7bG_VVnAT)


#### ui.Image

![Image UML](puml/actors/render/image.png)


## Dependencies

There are two dependencies that aren't necessary: returns and placeholder (both on the right edge). Code can always be rewritten to remove those two dependencies. That said, they don't introduce their own dependency tree, so only a total of three dependencies are added. Compared to the core dependencies (pixivpy, pixcat, and blessed), that's insignificant.

![dep tree](dependencies.png)

```sh
$ pipdeptree -v
2.0.0b1
$ pipdeptree --graph-output png -p koneko > dependencies.png
```

## Internal imports

See [import-analyzer](https://github.com/twenty5151/import-analyzer/)

* A larger score means it is a dependency of other modules more
    * "A dependency of a lot of modules"
* A smaller score means it depends on other modules more
    * "Depends on a lot of modules"
* A high proportion means most connections to other modules are its dependents
* A low proportion means most connections to other modules are its dependencies

|                 |   Dependents |   Dependencies |   Score |   Proportion |
|:----------------|-------------:|---------------:|--------:|-------------:|
| pure.py         |            9 |              0 |       9 |          100 |
| colors.py       |            2 |              0 |       2 |          100 |
| \_\_init\_\_.py |           15 |              0 |      15 |          100 |
| utils.py        |           12 |              2 |      10 |           86 |
| files.py        |            5 |              1 |       4 |           83 |
| config.py       |            8 |              2 |       6 |           80 |
| printer.py      |            6 |              2 |       4 |           75 |
| lscat.py        |            7 |              6 |       1 |           54 |
| api.py          |            3 |              3 |       0 |           50 |
| picker.py       |            3 |              4 |      -1 |           43 |
| cli.py          |            2 |              3 |      -1 |           40 |
| prompt.py       |            3 |              5 |      -2 |           38 |
| data.py         |            1 |              2 |      -1 |           33 |
| download.py     |            2 |              4 |      -2 |           33 |
| screens.py      |            2 |              6 |      -4 |           25 |
| main.py         |            2 |              7 |      -5 |           22 |
| lscat_prompt.py |            1 |              5 |      -4 |           17 |
| ui.py           |            2 |             12 |     -10 |           14 |
| assistants.py   |            1 |              7 |      -6 |           12 |
| lscat_app.py    |            1 |              8 |      -7 |           11 |
| \_\_main\_\_.py |            0 |              5 |      -5 |            0 |
