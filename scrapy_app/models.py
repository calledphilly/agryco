from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from agryco.scripts import sub_category

# creation de la base pour le modele de la table
Base = declarative_base()


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)

    sub_category = relationship('SubCategoryModele', back_populates='category')


class SubCategoryModel(Base):
    __tablename__ = 'sub_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    id_super_category = Column(Integer, ForeignKey('categories.id'))

    category = relationship('CategoryModele', back_populates='sub_category')
    product = relationship('ProductModele', back_populates='sub_category')


class ProductModel(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    description = Column(String)
    price = Column(String)
    id_super_category = Column(Integer, ForeignKey('sub_categories.id'))

    sub_category = relationship('SubCategoryModele', back_populates='product')


# "postgresql://user:password@localhost/database_name"
DATABASE_URL = "postgresql://root:root@localhost:5432/agryco_db"

# creation de l'engine
engine = create_engine(DATABASE_URL, echo=True)
# création des tables si elles n'existent pas déjà
Base.metadata.create_all(engine)
# création de la session a partir de l'engine
Session = sessionmaker(bind=engine)
