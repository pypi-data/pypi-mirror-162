Import project root path to `sys.path` for import local files.  

If you have a project with the following structure:  

```
| - my_proj
|
| - my_proj / config / models / account_model.py (class AccountModel)
|
| - my_proj / transaction / checker.py (class Checker)

```

Use ccrootpath to simplize your `import`:  

```
import ccrootpath
PROJECT_DIR = ccrootpath.set_project_root_path(__file__, 'my_proj')
from config.models.account_model import AccountModel
from transaction.checker import Checker
```