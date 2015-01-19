
import smtplib
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr

def InitSmtp(smtpHost, smtpUser, smtpPass):
	smtp = smtplib.SMTP(smtpHost)
	smtp.starttls()
	smtp.login(smtpUser, smtpPass)
	return smtp

def Send(smtp, fromEmail, toEmail, subject, body):
	body_charset = header_charset = "UTF-8"
	msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
	msg['From'] = formataddr((fromEmail, fromEmail))
	msg['To'] = formataddr((toEmail, toEmail))
	msg['Subject'] = Header(unicode(subject), header_charset)

	try:
		res = smtp.sendmail(fromEmail, toEmail, msg.as_string())
	except smtplib.SMTPException, e:
		print("Failed to send alert email!")
		raise
