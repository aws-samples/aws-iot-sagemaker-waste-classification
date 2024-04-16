SHELL := /bin/bash

.PHONY : help init config deploy iot-setup test lint nag clean delete
.DEFAULT: help

VENV_NAME ?= venv
PYTHON ?= $(VENV_NAME)/bin/python
AWS_CLI = $(VENV_NAME)/bin/aws
CONFIG_FILE = config.mk

ifneq ("$(wildcard $(CONFIG_FILE))","")
	include $(CONFIG_FILE)
endif

help:
	@echo "help	get the full command list"
	@echo "init	create VirtualEnv and install libraries"
	@echo "config	create configuration file"
	@echo "deploy	deploy CloudFormation stacks"
	@echo "test	run pre-commit checks"
	@echo "lint	GitHub actions cfn-lint test"
	@echo "nag	GitHub actions cfn-nag test"
	@echo "clean	delete VirtualEnv and installed libraries"
	@echo "delete	delete CloudFormation stacks"

# Initialize VirtualEnv
init: $(VENV_NAME) pre-commit

$(VENV_NAME): $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: requirements.txt
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -Ur requirements.txt
	touch $(VENV_NAME)/bin/activate

pre-commit: $(VENV_NAME)
	$(VENV_NAME)/bin/pre-commit install

clean:
	rm -rf "$(VENV_NAME)"
	find . -iname "*.pyc" -delete

# Generate configuration file
config:
ifneq ("$(wildcard $(CONFIG_FILE))","")
	@echo "File $(CONFIG_FILE) exists. Change configuration manually."
else
	@touch config.mk
	@read -p "AWS Region to create bucket in (e.g. us-east-1)?: " REGION && echo AWS_REGION=$$REGION >> $(CONFIG_FILE);
	@read -p "S3 Bucket name (e.g. s3-bucket-name)?: " BUCKET && echo BUCKET_NAME=$$BUCKET >> $(CONFIG_FILE);
	@read -p "CloudFormation Stack name (e.g. my-project-name)?: " STACK && echo STACK_NAME=$$STACK >> $(CONFIG_FILE);
	@echo "Configuration written to $(CONFIG_FILE) file."
endif

# Create S3 bucket
bucket:
	@$(AWS_CLI) s3 mb s3://$(BUCKET_NAME) \
	--region $(AWS_REGION)

# Build, Package, Deploy and Destroy
deploy: $(VENV_NAME) package
	@printf "\n--> Deploying %s template...\n" $(STACK_NAME)
	@$(VENV_NAME)/bin/aws cloudformation deploy \
	--template-file ./cfn/packaged.template \
	--stack-name $(STACK_NAME) \
	--region $(AWS_REGION) \
	--capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
	--parameter-overrides \
	  ArtefactsBucketName=$(BUCKET_NAME)

package: $(VENV_NAME) build
	@printf "\n--> Packaging and uploading templates to the %s S3 bucket ...\n" $(BUCKET_NAME)
	@$(VENV_NAME)/bin/aws cloudformation package \
  	--template-file ./cfn/main.template \
  	--s3-bucket $(BUCKET_NAME) \
  	--output-template-file ./cfn/packaged.template \
  	--region $(AWS_REGION)

build: $(VENV_NAME)
	@printf "\n--> Uploading artefacts to the %s S3 bucket ...\n" $(BUCKET_NAME)
	@$(VENV_NAME)/bin/aws s3 cp ./src/greengrass-app-components s3://$(BUCKET_NAME)/greengrass-app-components/ --recursive

delete:
	@printf "\n--> Deleting %s stack...\n" $(STACK_NAME)
	@$(VENV_NAME)/bin/aws cloudformation delete-stack \
            --stack-name $(STACK_NAME) \
            --region $(AWS_REGION)
	@printf "\n--> $(STACK_NAME) deletion has been submitted, check AWS CloudFormation Console for an update..."

# IOT device configuration
iot-setup:
	ci/fleet_provisioning_of_greengrass.sh $(STACK_NAME) $(AWS_REGION)

# Tests
test: $(VENV_NAME)
	$(VENV_NAME)/bin/pre-commit run --all-files

lint: $(VENV_NAME)
	$(VENV_NAME)/bin/cfn-lint cfn/**/*.template --ignore-checks=W3002

nag:
	cfn_nag_scan --input-path cfn

# cfn-publish specific
cfn-publish-package:
	zip -r packaged.zip -@ < ci/include.lst

# GitHub actions
test-cfn-lint:
	cfn-lint cfn/**/*.template --ignore-checks=W3002

test-cfn-nag:
	cfn_nag_scan --input-path cfn

version:
	@bumpversion --dry-run --list cfn/main.template | grep current_version | sed s/'^.*='//
