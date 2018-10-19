# Single Stream Audio Player Sample Skill (using ASK Python SDK)

This skill demonstrates how to create a single stream audio skill.  Single stream skills are typically used by radio stations to provide a convenient and quick access to their live stream.

User interface is limited to Play and Stop use cases.

## Usage

```text
Alexa, play my radio

Alexa, stop
```

## Installation

You will need to comply to the prerequisites below and to change a few configuration files before creating the skill and upload the lambda code.

### Pre-requisites

0. This sample uses the [ASK Python SDK](https://alexa-skills-kit-python-sdk.readthedocs.io/en/latest/) packages for developing the Alexa skill. 

    - If you already have the ASK Python SDK installed, then install the dependencies in the ``lambda/py/requirements.txt`` 
    using ``pip``. 
    - If you are starting fresh, follow the [Setting up the ASK SDK](https://alexa-skills-kit-python-sdk.readthedocs.io/en/latest/GETTING_STARTED.html) 
    documentation, to get the ASK Python SDK installed on your machine. We recommend you to use the 
    [virtualenv approach](https://alexa-skills-kit-python-sdk.readthedocs.io/en/latest/GETTING_STARTED.html#option-1-set-up-the-sdk-in-a-virtual-environment).
    Please run the following command in your virtualenv, to install the dependencies, before working on the skill code.

    ``
    pip install -r lambda/py/requirements.txt
    ``

1. You need an [AWS account](https://aws.amazon.com) and an [Amazon developer account](https://developer.amazon.com) to create an Alexa Skill.


### Code changes before deploying

1. ```./skill.json```

   Change the skill name, example phrase, icons, testing instructions etc ...

   Remember than most information is locale-specific and must be changed for each locale (en-GB, en-US etc.)

   Please refer to https://developer.amazon.com/docs/smapi/skill-manifest.html for details about manifest values.

2. ```./lambda/py/alexa/data.py```

   - Locale specific card data, radio URL, jingle URL has to be modified with correct runtime values.
   ```start_jingle``` is an optional property defining a Jingle to be played before the live stream. 
   Be sure to modify the value for each language supported by your skill.
   
   - When playing a jingle before your stream, you can choose the name of the database table where the "last played" 
   information will be stored.  If the table does not exist, the persistence code will create the table at the first 
   invocation of the skill. You can manually create the DynamoDB table with the following command:

    ```bash
    aws dynamodb create-table --table-name my_radio --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
    ```

        To minimize latency, we recommend to create the DynamoDB table in the same region as the Lambda function.
        
        When using DynamoDB, you also must ensure your Lambda function [execution role](http://docs.aws.amazon.com/lambda/latest/dg/intro-permission-model.html) will have permissions to read and write to the DynamoDB table.  Be sure [to add the following policy](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_manage_modify.html) to the Lambda function [execution role](http://docs.aws.amazon.com/lambda/latest/dg/intro-permission-model.html):
        
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "sid123",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:GetItem",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource": "arn:aws:dynamodb:us-east-1:YOUR_ACCOUNT_ID:table/my_radio"
                }
            ]
        }
        ```
   
3. Localization
 
    We use ``babel`` and python standard i18n ``gettext`` libraries, to create locale specific alexa responses.
   This [localization guide](https://github.com/alexa/skill-sample-python-fact/blob/master/instructions/localization.md) 
   explains in brief on how to localize your alexa responses. We have already localized this skill sample for multiple
   locales. If you want to make changes to the strings, follow these steps:
   
    - The base strings (eg: the strings wrapped in ``_()``) are present in ``./lambda/py/alexa/data.py`` module.
    - The message catalog ``data.pot`` is present in ``./lambda/py/alexa/locales`` directory.
    - The language specific translations (eg: ``data.po``) are present in ``./lambda/py/alexa/locales`` directory 
    as subfolders. The corresponding ``mo`` byte code files are also present in the same subfolder.
    - The localization interceptor has already been registered to the skill and can be checked in the 
    ``lambda/py/lambda_function.py`` module.
    - If you want to make any changes in the base strings, remember to generate the message catalog and the locale specific
    translations as mentioned in **Step 2** and **Step 3** of the guide.
    - If you only want to change the translations, generate the ``mo`` files for the translated strings, following
    the **Step 3** of the guide. 

4. ```./models/*.json```

   Change the model definition to replace the invocation name (it defaults to "my radio") and the sample phrases for each intent.  

   Repeat the operation for each locale you are planning to support.


### Deployment

For AWS Lambda to correctly execute the skill code, we need to zip the skill code along
with all dependencies and upload it. Follow the steps mentioned [here](https://alexa-skills-kit-python-sdk.readthedocs.io/en/latest/DEVELOPING_YOUR_FIRST_SKILL.html#preparing-your-code-for-aws-lambda)

## On Device Tests

To invoke the skill from your device, you need to login to the Alexa Developer Console, and enable the "Test" switch on your skill.

See https://developer.amazon.com/docs/smapi/quick-start-alexa-skills-kit-command-line-interface.html#step-4-test-your-skill for more testing instructions.

Then, just say :

```text
Alexa, open my radio.
```
