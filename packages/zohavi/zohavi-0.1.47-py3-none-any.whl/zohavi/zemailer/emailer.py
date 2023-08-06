import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header    import Header

from prepost import PreCond 
from zohavi.zbase.staple import ZStaple

class Emailer(ZStaple):
	####################################################

	@PreCond.dict_has_fields( config=[ 'HOST', 'PORT', 'SENDER', 'PASSWORD'])
	def __init__(self, config, logger=None):
		super().__init__(logger = logger )
		self.debug = True

		self.config  = config
		self.context = ssl.create_default_context()

	# @celeryJob.task(name="cjob.send_email")
	def send_email(self, subject, sender, recipients, text_body, html_body=None):
		with smtplib.SMTP_SSL( self.config['HOST'], self.config['PORT'], self.context ) as server:
			server.login( self.config['SENDER'] , self.config['PASSWORD'])

			if(html_body):
				msg = MIMEMultipart( "alternative" )
				msg.attach(  MIMEText(text_body, "plain") )
				msg.attach(  MIMEText(html_body, "html") )
			else:
				msg = MIMEText( text_body, 'plain', 'utf-8')
			
			msg['Subject'] = Header('email test', 'utf-8')
			msg['From'] = sender
			msg['To'] = ", ".join(  recipients )
			

			return server.sendmail( sender , recipients , msg.as_string() )

	# ####################################################
	# def generate_confirmation_token(email):
	# 	serializer = URLSafeTimedSerializer(self.config['SECRET_KEY'])
	# 	return serializer.dumps(email, salt=self.config['SECURITY_PASSWORD_SALT'])

	# ####################################################
	# def confirm_token(token, expiration=3600):
	# 	serializer = URLSafeTimedSerializer(self.config['SECRET_KEY'])
	# 	try:
	# 		email = serializer.loads(
	# 			token,
	# 			salt=self.config['SECURITY_PASSWORD_SALT'],
	# 			max_age=expiration
	# 		)
	# 	except:
	# 		return False
	# 	return email

	# ####################################################
	# # @celeryJob.task(name="cjob.send_email")
	# def send_register_email_confirmation(user):
	# 	token = generate_confirmation_token(user.email)
	# 	send_email.apply_async( args={ 'subject':' Confrim Your email',
	# 				'sender':self.config['MAIL_USERNAME'],
	# 				'recipients': [user.email],
	# 				'text_body':  render_template('zemail/confirm_email.txt',
	# 										user=user, token=token),
	# 				'html_body': render_template('zemail/confirm_email.html',
	# 										user=user, token=token) } )   


	
