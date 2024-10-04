module.exports = {
  apps : [{
    name: "my_app",
    script: "gunicorn",
    interpreter: "/root/venv/bin/python3.10",
    args: "-b 0.0.0.0:6969 app:app"
  }]
}