#!/bin/bash

# Script to check the actual status of python-mcp-server deployment
echo "🔍 Checking python-mcp-server Deployment Status"
echo "=============================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"
echo ""

# Check all deployments
echo "📋 All python-mcp-server deployments:"
kubectl get deployments --all-namespaces | grep python-mcp-server

echo ""
echo "📋 All pods with python-mcp-server:"
kubectl get pods --all-namespaces | grep python-mcp-server

echo ""
echo "📋 All services with python-mcp-server:"
kubectl get services --all-namespaces | grep python-mcp-server

echo ""
echo "🔍 Detailed pod information:"
kubectl get pods --all-namespaces -o wide | grep python-mcp-server

echo ""
echo "🔍 Pod labels and selectors:"
kubectl get pods --all-namespaces -l app=python-mcp-server -o yaml | grep -A 5 -B 5 "labels:"

echo ""
echo "🔍 Service selectors:"
kubectl get services --all-namespaces -o wide | grep python-mcp-server

echo ""
echo "📊 Namespace information:"
kubectl get namespaces | grep -E "(python-mcp|mcp-server)"

echo ""
echo "🔍 Events for python-mcp-server:"
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | grep python-mcp-server | tail -10