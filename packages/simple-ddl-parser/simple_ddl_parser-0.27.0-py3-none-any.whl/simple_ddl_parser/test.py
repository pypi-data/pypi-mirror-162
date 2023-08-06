from distutils.log import debug
from simple_ddl_parser import DDLParser
import pprint

results = DDLParser("""
CREATE TABLE [dbo].[OK_DopInf] (
    [id\DopInf]   INT           IDENTITY (1, 1) NOT NULL,
    [idEmployee] INT           NOT NULL,
    [DopInf]     VARCHAR (255) NOT NULL,
    CONSTRAINT [PK_OK_DopInf] PRIMARY KEY CLUSTERED ([idDopInf] ASC),
    CONSTRAINT [FK_OK_DopInf_Employee] FOREIGN KEY ([idEmployee]) REFERENCES [dbo].[Employee] ([id]) ON DELETE CASCADE ON UPDATE CASCADE
);
""").run(group_by_type=True)

pprint.pprint(results) 
