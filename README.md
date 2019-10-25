# Pocket commands for slack

These are [slack](https://slack.com/) commands to manipulate [pocket](https://getpocket.com/).

## Requirement

- [Docker](https://www.docker.com/)
  - docker-compose

## Usage

Lambda upload:

```console
$ docker-compose run awscli bash
> cd [COMMAND]/src
> lambda-uploader
```

## Install

Clone repository:

```console
$ git clone https://github.com/PiroHiroPiro/pocket_command_for_slack.git
$ cd pocket_command_for_slack
```

Build image:

```console
$ cp .env.example .env
$ cp ./source/[COMMAND]/lambda.json.example ./source/[COMMAND]/src/lambda.json
$ docker-compose build
```

## Command

### PICKUP

Get one item from the page saved in Pocket.

### STREAMING

Get items stored on pocket within 1 minute.

### UNIQUE

Delete items have duplicate URL from Pocket.

## Licence

This software is released under the MIT License, see [LICENSE](https://github.com/PiroHiroPiro/pocket_command_for_slack/blob/master/LICENSE).

## Author

[Hiroyuki Nishizawa](https://github.com/PiroHiroPiro)
