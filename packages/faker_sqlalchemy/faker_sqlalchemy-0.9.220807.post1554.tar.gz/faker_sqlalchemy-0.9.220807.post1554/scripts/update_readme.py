"""Updates the `README.rst` at the root of the repository with the latest documentation."""
import os
import sys

import jinja2


def main():
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
    sys.path.insert(0, base_dir)

    import faker_sqlalchemy

    template_path = os.path.join(base_dir, "README.j2.rst")
    with open(template_path) as f:
        content = f.read()

    template = jinja2.Template(content)
    result = template.render(
        **globals(),
        **locals(),
    )

    readme_path = os.path.join(base_dir, "README.rst")
    with open(readme_path, "w") as f:
        f.write(result)


if __name__ == '__main__':
    main()
