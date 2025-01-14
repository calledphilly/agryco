# from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, relationship

# # creation de la base pour le modele de la table
# Base = declarative_base()

# class CategoryModele(Base):
#     __tablename__ = "categories"
    
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     url = Column(String)
#     state = Column(String)
    
#     sub_category = relationship('SubCategoryModele', back_populates='category')

# class SubCategoryModele(Base):
#     __tablename__ = 'sub_categories'
    
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     url = Column(String)
#     state = Column(String)
#     id_super_category = Column(Integer, ForeignKey('categories.id'))
    
#     category = relationship('CategoryModele', back_populates='sub_category')
    
# # "postgresql://user:password@localhost/database_name"
# DATABASE_URL = "postgresql://root:root@localhost:5432/agryco_db"

# # creation de l'engine 
# engine = create_engine(DATABASE_URL, echo=True)
# # creation des tables si elles nexistent pas deja
# Base.metadata.create_all(engine)

# # creation de la session a partir de l'engine
# Session = sessionmaker(bind=engine)

