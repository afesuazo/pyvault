#!/bin/bash

uvicorn app.main:app --host 0.0.0.0 --port 4557 --reload --workers 3
