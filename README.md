# Groq Agents Assignment 1

## Overview
This project demonstrates a multi-agent Quality Assurance (QA) workflow built using Groq, LangGraph, and LnagChain.
The application reads a software requirement from a Markdown file and processes it through multiple AI agents to generate structured QA artifacts.

## Features
- Requirement Analysis
- Test Case Generation
- Security Review 
- QA Review
- Requirement input from a Markdown document
- Multi-agent workflow using LangGraph

## Setup

### 1. Create and activate a Python 3.11/3.12 virtual environment.

### 2. Install dependencies:

'''
pip install -U langchain==1.3.14 langchain-groq==1.1.3 langgraph==1.2.9 python-dotenv==1.2.2
'''

### 3. Add your Groq API key to your environment or a .env file:

'''
GROQ_API_KEY=your-api-key
'''

## Run
python run_groq_qa.py

