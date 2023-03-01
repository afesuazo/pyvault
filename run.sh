#!/bin/bash

gunicorn app.main:app -k uvicorn.workers.UvicornWorker