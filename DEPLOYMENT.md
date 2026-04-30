# Deployment Notes

## Render example

1. Create a new Web Service.
2. Connect this repository.
3. Set build command:

```bash
pip install -r requirements.txt
```

4. Set start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Add environment variables from `.env.example`.

## Private key handling

For hosted deployment, prefer `GITHUB_PRIVATE_KEY` as an environment variable.

Some platforms require newlines to be stored as literal `\n` characters. This app converts `\n` back into real newlines automatically.

## Local key handling

For local development, save your GitHub App private key as `private-key.pem` and set:

```bash
GITHUB_PRIVATE_KEY_PATH=private-key.pem
```

Do not commit the private key.
