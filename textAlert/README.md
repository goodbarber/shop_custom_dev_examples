# Order text alerts
Service which will notify customers of newly arrived online orders

## Setting up the systemd daemon

Place the `gbTextAlert.service` in your systemd unit files directory

Change `ConditionPathExists`, `WorkingDirector` and `ExecStart` to the path where the repo is stored on your filesystem

Then, run:
```bash
$ sudo systemctl daemon-reload
$ sudo systemctl start gbTextAlert
```
