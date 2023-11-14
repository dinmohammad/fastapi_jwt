async def get_user_by_email(email: str, db, models):
    user = db.query(models).filter(models.email == email).first()
    return user