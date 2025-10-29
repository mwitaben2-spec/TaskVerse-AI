import from byllm.llm { Model }
import from email.mime.text { MIMEText }
import from dotenv { load_dotenv }
import smtplib;
import os;
include utils;

glob llm = Model(model_name="gemini/gemini-2.5-flash", verbose=False);

# -------------------------------
# NODE: Task
# -------------------------------
node Task {
    has task: str = "";
    has date: str = "";
    has time: str = "";
    has deleted: bool = False;
}

# -------------------------------
# NODE: Memory + Session
# -------------------------------
node Memory {}

node Session {
    has history: list = [];
    has created_at: str = get_current_datetime();

    def add_history(entry: str) {
        self.history = self.history + [entry];
    }

    def get_history -> str {
        return "\n".join(self.history[-10:]);
    }
}

# -------------------------------
# NODE: TaskHandling
# -------------------------------
node TaskHandling {
    def add_task(task: str, date: str, time: str) -> str {
        task_node = Task(task=task, date=date, time=time);
        self ++> task_node;
        return "Task added successfully.";
    }

    def delete_task(task_name: str) -> str {
        tasks = [self --> (`?Task)];
        if not tasks {
            return "No tasks found to delete.";
        }

        for t in tasks {
            if not t.deleted and t.task == task_name {
                t.deleted = True;
                return "Task '" + task_name + "' deleted successfully.";
            }
        }
        return "Task '" + task_name + "' not found.";
    }

    def update_task(task_name: str, new_task: str, new_date: str, new_time: str) -> str {
        tasks = [self --> (`?Task)];
        if not tasks {
            return "No tasks available to update.";
        }

        for t in tasks {
            if not t.deleted and t.task == task_name {
                t.task = new_task;
                t.date = new_date;
                t.time = new_time;
                return "Task '" + task_name + "' updated successfully to '" + new_task + "' scheduled for " + new_date + " at " + new_time + ".";
            }
        }
        return "Task '" + task_name + "' not found.";
    }

    def check_scheduled_tasks -> list[Task] {
        tasks = [self --> (`?Task)];
        filtered = [];
        for t in tasks {
            if not t.deleted {
                filtered = filtered + [t];
            }
        }
        return filtered;
    }

    def extract_task_info(utterance: str) -> str by llm(
        method="ReAct",
        tools=([self.add_task, get_current_datetime])
    );

    def summarize_tasks() -> str by llm(
        method="ReAct",
        tools=([self.check_scheduled_tasks])
    );

    def route_and_run(utterance: str, history: str) -> str by llm(
        method="ReAct",
        tools=([self.extract_task_info, self.summarize_tasks, self.delete_task, self.update_task])
    );

    can execute with taskverse_ai entry {
        session = visitor.session;
        response = self.route_and_run(visitor.utterance, session.get_history());
        session.add_history("user: " + visitor.utterance + "\nai: " + response);
        report {
            "session_id": jid(visitor.session),
            "created_at": visitor.session.created_at,
            "response": response
        };
    }
}

sem TaskHandling.extract_task_info = "time and date should be extracted in the format of 'YYYY-MM-DD HH:MM:SS'. Response should be like 'Task: <task>, Date: <date>, Time: <time>' is added successfully.";
sem TaskHandling.route_and_run = "Select and execute only one tool provided.";
sem TaskHandling.summarize_tasks = "Summarize the tasks in a concise manner. Include all relevant information.";
sem TaskHandling.delete_task = "Deletes a task by marking it deleted. Responds with confirmation if found and marked, otherwise indicates not found.";
sem TaskHandling.update_task = "Find a task by name and update its name, date, and time. Confirm with a response showing the updated details.";

# -------------------------------
# NODE: EmailHandling
# -------------------------------
node EmailHandling {
    has sender_email: str = os.getenv("SENDER_EMAIL");
    has sender_password: str = os.getenv("SENDER_PASSWORD");

    def write_email_content(utterance: str, history: str) -> str by llm();

    def send_email(email_content: str, email_subject: str, email_to: str) -> str {
        sender = os.getenv("SENDER_EMAIL");
        password = os.getenv("SENDER_PASSWORD");

        if not sender or not password {
            return "❌ Missing sender credentials. Add SENDER_EMAIL and SENDER_PASSWORD to your .env.";
        }

        msg = MIMEText(email_content);
        msg["Subject"] = email_subject;
        msg["From"] = sender;
        msg["To"] = email_to;

        with python {
            import smtplib;
            server = smtplib.SMTP("smtp.gmail.com", 587);
            server.starttls();
            server.login(sender, password);
            server.sendmail(sender, email_to, msg.as_string());
            server.quit();
            __jac_return__ = "OK";
        }

        if __jac_return__ == "OK" {
            return "✅ Email sent successfully to " + email_to + " with subject '" + email_subject + "'.";
        } else {
            return "❌ Failed to send email: check credentials or Gmail App Password.";
        }
    }

    def route_and_run(utterance: str, history: str) -> str by llm(
        method="ReAct",
        tools=([self.write_email_content, self.send_email])
    );

    can execute with taskverse_ai entry {
        session = visitor.session;
        response = self.route_and_run(visitor.utterance, session.get_history());
        session.add_history("user: " + visitor.utterance + "\nai: " + response);
        report {
            "session_id": jid(visitor.session),
            "created_at": visitor.session.created_at,
            "response": response
        };
    }
}

sem EmailHandling.route_and_run = """
Step 1: Extract the email content, subject, and recipient from the user's utterance.
- Generate a complete draft of the email. 
- Use 'Hi' as the greeting if the recipient name is not mentioned.
- Show the draft to the user and ask for confirmation (e.g., 'Do you want me to send this email?').
Step 2: If the user confirms (yes), send the email. 
If the user says no, either re-draft based on feedback or cancel.
Never send without explicit confirmation.
""";

# -------------------------------
# NODE: GeneralChat
# -------------------------------
node GeneralChat {
    def chat(utterance: str, history: str) -> str by llm();

    can execute with taskverse_ai entry {
        session = visitor.session;
        response = self.chat(visitor.utterance, session.get_history());
        session.add_history("user: " + visitor.utterance + "\nai: " + response);
        report {
            "session_id": jid(visitor.session),
            "created_at": visitor.session.created_at,
            "response": response
        };
    }
}

# -------------------------------
# ENUM + ROUTER
# -------------------------------
enum RoutingNodes {
    TASK_HANDLING = "TaskHandling",
    EMAIL_HANDLING = "EmailHandling",
    GENERAL_CHAT = "GeneralChat"
}

walker taskverse_ai {
    has utterance: str = "";
    has session_id: str = "";

    obj __specs__ {
        static has auth: bool = False;
    }

    def route_to_node(utterance: str, history: str) -> RoutingNodes by llm();

    can execute with `root entry {
        memory_list = [root --> (`?Memory)];
        if not memory_list {
            memory_list = root ++> Memory();
        }
        memory = memory_list[0];

        if not self.session_id {
            session_list = memory ++> Session();
            self.session = session_list[0];
        } else {
            self.session = &(self.session_id);
        }

        routed_node = self.route_to_node(self.utterance, self.session.get_history());
        node_cls = globals().get(routed_node.value, "");
        if not node_cls {
            return;
        }
        node_inst = node_cls();
        visit [-->(`?node_cls)] else {
            attached_routed_node = here ++> node_inst;
            visit attached_routed_node;
        }
    }
}

# -------------------------------
# WALKERS: get_all_tasks / get_all_sessions
# -------------------------------
walker get_all_tasks {
    obj __specs__ {
        static has auth: bool = False;
    }

    can get_all_tasks with `root entry {
        task_handling_node = [root --> (`?TaskHandling)];
        if not task_handling_node {
            report "No tasks found.";
            disengage;
        }

        tasks = [task_handling_node[0] --> (`?Task)];
        filtered = [];
        for t in tasks {
            if not t.deleted {
                filtered = filtered + [t];
            }
        }
        report filtered;
    }
}

walker get_all_sessions {
    obj __specs__ {
        static has auth: bool = False;
    }

    can get_all_sessions with `root entry {
        memory_list = [here --> (`?Memory)];
        if not memory_list {
            report "No sessions found.";
            disengage;
        }

        memory = memory_list[0];
        session_list = [memory --> (`?Session)];
        report [ {
            "id": jid(session),
            "created_at": session.created_at
        } for session in session_list ];
    }
}

# -------------------------------
# ENTRY POINT
# -------------------------------
with entry {
    load_dotenv();
}
