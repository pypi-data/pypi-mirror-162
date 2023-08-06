# gruzau

gruzau - система плагинов для uzoenr

## Лицензия (GNU GPL 3+)

````
gruzau - Plugins for uzoenr
Copyright (C) 2022 sherekhan
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
````

## Использование

### gruzau-dump

Предназначен для объединения веб-страниц в единый текстовый
файл в UTF-8.

`gruzau-dump <enc> <output-file> <input files>`


### gruzau-load

Предназначен для объединения множества ссылок в единый файл.

`gruzau-load <output-file> <liks-list-file>`

### gruzau-speak

Предназначен для синтеза речи. 
Использует espeak.

`gruzau-speak <file>`