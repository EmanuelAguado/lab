import os
import json

from ayon_applications import PreLaunchHook
import gazu

class PreKitsuStatusChange(PreLaunchHook):
    """
    Pre-launch hook that changes the Kitsu task status before launching an application.

    It checks environment variables, reads project settings, evaluates conditions,
    connects to Kitsu using gazu, and updates the task status if allowed.
    """
    order = 1
    launch_types = set()

    def execute(self):
        if "KITSU_LOGIN" not in os.environ:
            self.log.info(
                "KITSU_LOGIN is not set. assuming rendeing in deadline. Skipping status."
                )
            return

        data = self.launch_context.data

        project_settings = data["project_settings"]["labstudio"]["PRODUCTION"]["StartStatusChange"]

        if project_settings["enabled"]:
            self.log.info("Kitsu Status change is Enabled.")
        else:
            self.log.info("Kitsu Status change is disabled.")
            return

        if not project_settings["app_start_status_shortname"]:
            self.log.info("App starting status in not configured")
            return
        
        app_start_status_shortname = project_settings["app_start_status_shortname"]

        status_conditions = []
        if project_settings["app_startstatus_change_conditions"]:
            status_conditions= project_settings["app_startstatus_change_conditions"]
        else:
            self.log.info("Status change condotions are empty")

        gazu.set_host(os.environ["KITSU_SERVER"])
        gazu.log_in(os.environ["KITSU_LOGIN"], os.environ["KITSU_PWD"])

        if not self.data["task_entity"]["data"].get("kitsuId"):
            self.log.info("This task does not have a kitsu task id. Skipping kitsu task status change.")
            return

        kitsuId = self.data["task_entity"]["data"]["kitsuId"]
        task=gazu.task.get_task(kitsuId)
        task_current_status_shortname = task["task_status"]["short_name"]

        allow_status_change = True
        for status_cond in status_conditions:
            condition = status_cond["condition"] == "equal"
            match = task_current_status_shortname in status_cond["short_name"]
            if match and not condition or condition and not match:
                allow_status_change = False
                break

        if allow_status_change:
            if not gazu.task.get_task_status_by_short_name(app_start_status_shortname):
                self.log.info("Failed to recieve kitsu status instance for shortname. Skipping Status change.")
                return
            new_kitsu_status = gazu.task.get_task_status_by_short_name(app_start_status_shortname)

            self.log.info(f"Current Kitsu task status is {task_current_status_shortname}. Task id {kitsuId}")
            self.log.info(f"Changing Kitsu task status to {app_start_status_shortname}.")

            gazu.task.add_comment(task["id"], new_kitsu_status)
        else:
            self.log.info(f"Status not changed due to conditions: {status_conditions}")
        gazu.log_out()