import imaplib

try:
    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login("baradok609@gmail.com", "Jiji987290!x")
    print("IMAP LOGIN OK")
    m.select("INBOX")
    _, ids = m.search(None, "ALL")
    print("mails:", len((ids[0] or b"").split()))
    m.logout()
except Exception as e:
    print("IMAP FAIL:", str(e)[:200])
