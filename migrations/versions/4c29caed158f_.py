"""empty message

Revision ID: 4c29caed158f
Revises: 
Create Date: 2018-10-11 14:24:11.921299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c29caed158f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('web_page', sa.String(length=100), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('web_page')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nickname', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('surname', sa.String(length=40), nullable=False),
    sa.Column('education', sa.String(length=40), nullable=True),
    sa.Column('linkedin', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('gender', sa.String(length=20), nullable=False),
    sa.Column('phone', sa.Integer(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('last_jobapp_read', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('nickname')
    )
    op.create_table('build',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('specification', sa.String(length=2000), nullable=False),
    sa.Column('category', sa.String(length=200), nullable=False),
    sa.Column('worth', sa.Integer(), nullable=False),
    sa.Column('place', sa.String(length=200), nullable=False),
    sa.Column('post_date', sa.DateTime(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.Column('creater_id', sa.Integer(), nullable=True),
    sa.Column('contractor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['contractor_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['creater_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('employee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('company', sa.Integer(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('position', sa.String(length=100), nullable=False),
    sa.Column('salary', sa.Integer(), nullable=True),
    sa.Column('date_join', sa.DateTime(), nullable=True),
    sa.Column('emp_mail', sa.String(length=200), nullable=True),
    sa.Column('emp_tel', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('employees',
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.Column('build_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], ),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], )
    )
    op.create_table('job_app',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('offer_sender', sa.Integer(), nullable=True),
    sa.Column('offer_recipient', sa.Integer(), nullable=True),
    sa.Column('salary', sa.Integer(), nullable=False),
    sa.Column('date_send', sa.DateTime(), nullable=True),
    sa.Column('position', sa.String(length=100), nullable=False),
    sa.Column('company', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company'], ['company.id'], ),
    sa.ForeignKeyConstraint(['offer_recipient'], ['user.id'], ),
    sa.ForeignKeyConstraint(['offer_sender'], ['employee.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_app_timestamp'), 'job_app', ['timestamp'], unique=False)
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=200), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('build_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('private_company', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], ),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_timestamp'), 'post', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_post_timestamp'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_job_app_timestamp'), table_name='job_app')
    op.drop_table('job_app')
    op.drop_table('employees')
    op.drop_table('followers')
    op.drop_table('employee')
    op.drop_table('build')
    op.drop_table('user')
    op.drop_table('company')
    # ### end Alembic commands ###