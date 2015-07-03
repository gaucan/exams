from functools import wraps
from flask import abort, g ,redirect, url_for
from flask.ext.login import current_user
from app.models import Student,UcitelPredmetu

	
def permission_required():
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if current_user.is_anonymous():
				# abort(403)
			    return redirect(url_for('auth.login'))

			s=Student.query.filter_by(user_id=current_user.id).first()
			if  s is None:
				abort(403)

			g.student=current_user.students[0] #prvy student kt je priradeny k userovi

			return f(*args, **kwargs)
		return decorated_function
	return decorator

def student_required(f):
	return permission_required()(f)

# def permission_required(permission):
# 	def decorator(f):
# 		@wraps(f)
# 		def decorated_function(*args, **kwargs):
# 			if not current_user.can(permission):
# 				abort(403)
# 			return f(*args, **kwargs)
# 		return decorated_function
# 	return decorator

# def admin_required(f):
# 	return permission_required(Permission.ADMINISTER)(f)