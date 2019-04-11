#!/bin/sh

set -e

kong migrations bootstrap
kong start