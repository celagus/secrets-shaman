SHAMAN_ROLE_NAME = "" # it must be created in all accounts, it must have proper privileges for lambda, ec2 and organizations (only in main account) and it must have trust policy for lambda role
ORG_ACCOUNT_ID = "" # it must be the main account for AWS Organizations
POWER_REGEX = r"(?i)\b(secret[-_]key|key[_-][a-z0-9]*|access[-_]key[-_]id|token|password|secret|[a-z0-9]*[_-]key|[a-z0-9]*[_-]token|token[_-][a-z0-9]*)\b[\s:=\'\"]*([A-Za-z0-9!@#$%^&*()_+\-={}\[\]|\\:;\"\',.<>?\/]{0,})\b"
REGIONS = [
    "us-east-1",
    "us-east-2"
]