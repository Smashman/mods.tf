def get_or_create(session, model, create_args=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        if create_args:
            kwargs.update(create_args)
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance