#  layerd

Mount and Inspect Lambda Layers on the fly.

> Lambda Layers created by a third party?
>
> Need to check what was uploaded?
>
> Use `layerd`.


# Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration](#Configuration)


# Inspiration

    

# Installation

    $ pip3 install layerd


# Usage


#### CLI

The `layerd` script is automatically added to your OS's Path.
Call it with an ARN of a public lambda layer to mount the layer.

    $ layerd <ARN>

Example:

    $ layerd arn:aws:lambda:us-east-1:ACC:layer:LAYER-NAME:221

    Layer:    LAYER-NAME
    Region:   us-east-1
    V:        221

    Created: ./LAYER-NAME-221/

And pulled, unzipped, and mounted is the contents of the Lambda Layer.

    $ tree
    .
    └── LAYER-NAME-221/
        └── ...


#### Python Inline

Very Simply: The `layerd` module has a `layerd(arn: str)` function to mount a Lambda Layer.


    >>> from layerd import layerd

    >>> layerd('arn:aws:lambda:us-east-1:ACC:layer:LAYER-NAME:335')
    Layer:    LAYER-NAME
    Region:   us-east-1
    V:        335

    Created: ./layer-cisco-otel-lambda-1/


Boom. You've mounted the Layer locally.


# Configuration

Environment Variables are used to handle Configurations.
