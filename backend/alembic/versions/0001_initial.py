"""Create LogiCraft core normalized tables."""
from alembic import op
import sqlalchemy as sa
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("users", sa.Column("id",sa.Integer,primary_key=True), sa.Column("email",sa.String(190),nullable=False,unique=True), sa.Column("full_name",sa.String(120),nullable=False), sa.Column("role",sa.String(30),nullable=False), sa.Column("password_hash",sa.String(255),nullable=False), sa.Column("active",sa.Boolean,nullable=False,server_default=sa.true()))
    op.create_index("ix_users_role","users",["role"])
    op.create_table("records",sa.Column("id",sa.Integer,primary_key=True),sa.Column("module",sa.String(50),nullable=False),sa.Column("name",sa.String(180),nullable=False),sa.Column("status",sa.String(40),nullable=False),sa.Column("reference",sa.String(100),nullable=False),sa.Column("location",sa.String(180),nullable=False),sa.Column("quantity",sa.Float,nullable=False),sa.Column("updated_at",sa.DateTime,nullable=False))
    for col in ("module","name","status"): op.create_index("ix_records_"+col,"records",[col])
    op.create_table("record_attributes",sa.Column("record_id",sa.Integer,sa.ForeignKey("records.id",ondelete="CASCADE"),primary_key=True),sa.Column("attribute",sa.String(100),primary_key=True),sa.Column("attribute_value",sa.JSON,nullable=True))
    op.create_index("ix_record_attributes_attribute","record_attributes",["attribute"])
    op.create_table("status_events",sa.Column("id",sa.Integer,primary_key=True),sa.Column("record_id",sa.Integer,sa.ForeignKey("records.id",ondelete="CASCADE"),nullable=False),sa.Column("status",sa.String(40),nullable=False),sa.Column("note",sa.Text,nullable=False),sa.Column("created_at",sa.DateTime,nullable=False))
    op.create_index("ix_events_record","status_events",["record_id"])
    op.create_table("fuel_logs",sa.Column("id",sa.Integer,primary_key=True),sa.Column("vehicle_id",sa.Integer,sa.ForeignKey("records.id"),nullable=False),sa.Column("liters",sa.Float,nullable=False),sa.Column("odometer_km",sa.Float,nullable=False),sa.Column("cost",sa.Float,nullable=False),sa.Column("filled_at",sa.DateTime,nullable=False))
    op.create_index("ix_fuel_vehicle","fuel_logs",["vehicle_id"])
def downgrade():
    op.drop_table("fuel_logs"); op.drop_table("status_events"); op.drop_table("record_attributes"); op.drop_table("records"); op.drop_table("users")
