# Pocket command for slack

These are [slack](https://slack.com/) command to manipulate [pocket](https://getpocket.com/).

## Requirement

- Python:3.6
- Pipenv:2018.11.26 or later

## Command
### CLEAN

Deletes an item with a link to Twitter from the items stored on Pocket.
Remove "twitter" tags from items with multiple tags stored on Pocket.
Currently not used.

### PICKUP

Get one item from the page saved in Pocket.

### RESET

Deletes up to 3000 items given the "twitter" tag from Pocket.
Currently not used.

### SELECT

Remove the "twitter" tag and add the "selected_qiita" tag to the item whose number of likes is 100 or more from the Qiita page stored in Pocket.
Currently not used.

### STREAMING

Get items stored on pocket within 1 minute.

## Install

Clone repository:

```console
$ git clone https://github.com/PiroHiroPiro/pocket_command_for_slack.git
$ cd pocket_command_for_slack
```

Install libraries:

```console
$ pipenv install
$ pipenv shell
```

Move to directory of desired command:

```console
$ cd [clean | pickup | reset | select | streaming]
```

Copy configuration file:

```console
$ cp lambda.json.example ./src/lambda.json
```

Enter the Lambda function name, roles, environment variables, etc. in the copied configuration file `lambda.json`:

Upload to Lambda:

```console
$ cd src
$ lambda-uploader
```

## Licence

This software is released under the MIT License, see [LICENSE](https://github.com/PiroHiroPiro/pocket_command_for_slack/blob/master/LICENSE).

## Author

[Hiroyuki Nishizawa](https://github.com/PiroHiroPiro)
