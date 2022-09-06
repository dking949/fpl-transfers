# FPL Transfers
This project is a joint collaboration between mates (James & Darren) and fantasy football rivals.
Fantasy Premier league: (https://fantasy.premierleague.com/) is a fantasy football game played by over 10 million players worldwide.
We play every year and are in a pretty competitive mini league with some other mates.

This project analyses the transfers made by each player each gameweek to see who made the best and worst transfers. It then shows these transfers on web app for all to see just how good (or poor) your managerial knowledge is compared to your mates.

## Background
The idea was the brainchild of James. He wrote a Python script that would send an email blast to all members of the mini league with the gameweeks transfer results. Together we repurposed this a little bit and turned it into an API hosted on AWS using Serverless (https://www.serverless.com/).
In a seperate repo I have created a React frontend app to display the data: https://github.com/dking949/fpl-transer-abuse-frontend

## Technologies Used
- Python
- Serverless
- AWS Lambda
- AWS Systems manager

## Code Structure

### Deployment (via serverless)

To deploy to serverless, run
```
$ serverless deploy
```

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function hello
```

Alternatively, it is also possible to emulate API Gateway and Lambda locally by using `serverless-offline` plugin. In order to do that, execute the following command:

```bash
serverless plugin install -n serverless-offline
```

It will add the `serverless-offline` plugin to `devDependencies` in `package.json` file as well as will add it to `plugins` in `serverless.yml`.

After installation, you can start local emulation with:

```
serverless offline
```

To learn more about the capabilities of `serverless-offline`, please refer to its [GitHub repository](https://github.com/dherault/serverless-offline).

### Bundling dependencies

In case you would like to include 3rd party dependencies, you will need to use a plugin called `serverless-python-requirements`. You can set it up by running the following command:

```bash
serverless plugin install -n serverless-python-requirements
```

Running the above will automatically add `serverless-python-requirements` to `plugins` section in your `serverless.yml` file and add it as a `devDependency` to `package.json` file. The `package.json` file will be automatically created if it doesn't exist beforehand. Now you will be able to add your dependencies to `requirements.txt` file (`Pipfile` and `pyproject.toml` is also supported but requires additional configuration) and they will be automatically injected to Lambda package during build process. For more details about the plugin's configuration, please refer to [official documentation](https://github.com/UnitedIncome/serverless-python-requirements).
