# cpsc449-fall2023-project4
CPSC 449 - Fall 2023 - Project 3 - Polyglot Persistence and Functional Partitioning

Project members:



# Development

1. Set working directory as this project's directory

2. Create and enter virtual environment

   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```

3. Install requirements

   ```bash
   pip install -r requirements.txt
   ```

4. Configure Redis CLI

   You will need to have Redis CLI installed and running on the system at port 6379. You can verify this by running the following command:

   ```bash
   redis-cli ping
   ```

   Otherwise install redis:
   ```bash
   sudo apt update
   sudo apt install --yes redis
   ```

5. Configure AWS CLI

   You will need to follow the instructions on the Long-term credentials tab of [Configuring using AWS CLI commands](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html#getting-started-quickstart-new-command) to configure dummy credentials for DynamoDB local.


6. Start API

   ```bash
   foreman start --formation users-primary=1,users-secondary=1,users-tertiary=1,enrollment=3,krakend=1,amazon-dynamodb-local=1
   ```

7. Initialize databases
   
   If databases haven't been initialized yet (ie. this is the first run), run the following **after running one of the commands above, which activates the LiteFS replication service**:

   ```bash
   ./bin/init.sh
   ```

   You may also wish to run this in development to reset the database, especially if a schema has been changed.
