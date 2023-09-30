import os
print("Current working directory:", os.getcwd())

# Define the path to the .env file
env_path = '\db.env'

if os.path.exists(env_path):
    print(".env file exists!")
else:
    print(".env file not found!")

# Read the contents of the .env file
with open(env_path, 'r') as file:
    data = file.read()

# Print the contents
print("Contents of .env file:")
print(data)

# Optionally modify the data (uncomment the following line to add an example entry)
# data += "\nEXAMPLE_KEY=example_value"

# Save (write) the data back to the .env file
with open(env_path, 'w') as file:
    file.write(data)

print("Data saved successfully!")
