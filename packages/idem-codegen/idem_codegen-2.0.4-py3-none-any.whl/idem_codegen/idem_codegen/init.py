def __init__(hub):
    # Remember not to start your app in the __init__ function
    # This function should just be used to set up the plugin subsystem
    # The run.py is where your app should usually start
    hub.pop.sub.load_subdirs(hub.idem_codegen, recurse=True)
    hub.idem_codegen.RUNS = {}
    hub.pop.sub.add(dyne_name="tf_idem")
    hub.pop.sub.add(dyne_name="discovery")


def cli(hub):
    hub.pop.config.load(["idem_codegen"], cli="idem_codegen")
    # Your app's options can now be found under hub.OPT.idem_codegen
    kwargs = dict(hub.OPT.idem_codegen)
    hub.test = None

    # Initialize the asyncio event loop
    hub.pop.loop.create()

    # Start the async code
    coroutine = hub.idem_codegen.init.run(**kwargs)
    hub.pop.Loop.run_until_complete(coroutine)


async def run(hub, **kwargs):
    global run_name
    try:
        if hub.test:
            run_name = hub.test.idem_codegen.run_name
        elif hub.SUBPARSER == "generate":
            if (
                hub.OPT.idem_codegen.type
                not in hub.idem_codegen.tool.utils.ACCEPTABLE_GENERATE_TYPES
            ):
                raise ValueError("Invalid value of parameter 'type'")
            hub.log.info("Idem Resource Id files Generation started")
            hub.tf_idem.exec.generate_resource_ids_from_tf_state.init()
            hub.log.info("Idem Resource Id files Generation completed")
            return
        elif hub.SUBPARSER in ["discovery", "tf_idem"]:
            hub.log.info(
                f"Idem Codegen {hub.SUBPARSER} started",
            )
            run_name = hub.SUBPARSER
        else:
            raise ValueError("Invalid value of parameter 'run_name'")
    except Exception as e:
        hub.log.error(e)
        return

    """
    This is the entrypoint for the async code in your project
    """
    hub.log.info("Validate phase started")
    hub.idem_codegen.validator.init.validate(run_name)
    hub.log.info("Validate phase completed successfully")

    hub.log.info("Compile phase started")
    hub.idem_codegen.compiler.init.compile(run_name)
    hub.log.info("Compile phase completed successfully")

    # Preprocessing is completed now. Starting with file by file conversion for each module in cluster
    hub.log.info("Group phase started")
    output_dir_path = hub.idem_codegen.group[
        hub.OPT.idem_codegen.group_style
    ].segregate(run_name)
    hub.log.info("Group phase completed successfully")

    # Generation Phase
    hub.idem_codegen.generator.init.run(run_name, output_dir_path)
    hub.log.info("Idem Code Generation completed")
