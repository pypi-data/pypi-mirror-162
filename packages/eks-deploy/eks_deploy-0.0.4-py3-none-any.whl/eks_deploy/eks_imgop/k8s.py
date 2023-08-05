#!/bin/python3
import os


def delete_k8s(fileName):
    command = "kubectl delete -f "+ fileName
    os.system(command)

def apply_k8s(fileName):
    command="kubectl apply -f " + fileName
    os.system(command)
