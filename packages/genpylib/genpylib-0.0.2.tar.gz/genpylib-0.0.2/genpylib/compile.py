import jinja2
import json
import yaml
import os


def compile_template(config, template_path, dump_path):
    with open(template_path, "r") as f:
        template = f.read()

    template_obj = jinja2.Template(template)
    rendered_template = template_obj.render(config)
    rendered_template = os.linesep.join(
        [s for s in rendered_template.splitlines() if s.strip()]
    )

    with open(dump_path, "w") as f:
        f.write(rendered_template)


if __name__ == "__main__":
    main()
