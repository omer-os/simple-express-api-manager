import os
import json
import shutil
import subprocess
import pyperclip

class ExpressProjectGenerator:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_path = os.path.join(os.getcwd(), project_name)
        self.src_path = os.path.join(self.project_path, 'src')
        self.database_url = ""

    def create_project(self):
        self._create_directory_structure()
        self._initialize_npm_project()
        self._setup_typescript()
        self._setup_prisma()
        self._create_base_files()
        self._install_dependencies()
        self._generate_prisma_client()
        self._copy_script()
        print(f"Project '{self.project_name}' created successfully!")

    def _create_directory_structure(self):
        directories = [
            self.src_path,
            os.path.join(self.src_path, 'controllers'),
            os.path.join(self.src_path, 'routes'),
            os.path.join(self.src_path, 'services'),
            os.path.join(self.src_path, 'middlewares'),
            os.path.join(self.src_path, 'models'),
            os.path.join(self.src_path, 'config'),
            os.path.join(self.src_path, 'utils'),
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _initialize_npm_project(self):
        os.chdir(self.project_path)
        package_json = {
            "name": self.project_name,
            "version": "1.0.0",
            "description": "Express TypeScript project with Prisma",
            "main": "dist/server.js",
            "scripts": {
                "start": "node dist/server.js",
                "dev": "ts-node-dev --respawn --transpile-only src/server.ts",
                "build": "tsc",
                "prisma:generate": "prisma generate",
                "prisma:migrate": "prisma migrate dev"
            },
            "keywords": ["express", "typescript", "prisma"],
            "author": "",
            "license": "ISC",
            "dependencies": {
                "express": "^4.17.1",
                "@prisma/client": "^3.15.2",
                "dotenv": "^10.0.0",
                "cors": "^2.8.5",
                "helmet": "^4.6.0",
                "express-async-errors": "^3.1.1"
            },
            "devDependencies": {
                "typescript": "^4.5.4",
                "@types/node": "^16.11.12",
                "@types/express": "^4.17.13",
                "@types/cors": "^2.8.12",
                "ts-node-dev": "^1.1.8",
                "prisma": "^3.15.2"
            }
        }
        with open('package.json', 'w') as f:
            json.dump(package_json, f, indent=2)

    def _setup_typescript(self):
        tsconfig = {
            "compilerOptions": {
                "target": "es2017",
                "module": "commonjs",
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules"]
        }
        with open(os.path.join(self.project_path, 'tsconfig.json'), 'w') as f:
            json.dump(tsconfig, f, indent=2)

    def _setup_prisma(self):
        self.database_url = input("database URL for Prisma: ")
        schema_path = os.path.join(self.project_path, 'prisma', 'schema.prisma')
        os.makedirs(os.path.dirname(schema_path), exist_ok=True)
        schema_content = f"""
generator client {{
  provider = "prisma-client-js"
}}

datasource db {{
  provider = "postgresql"
  url      = env("DATABASE_URL")
}}

model User {{
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}}
"""
        with open(schema_path, 'w') as f:
            f.write(schema_content.strip())

    def _create_base_files(self):
        self._create_file('src/app.ts', self._get_app_content())
        self._create_file('src/server.ts', self._get_server_content())
        self._create_file('src/config/database.ts', self._get_database_config_content())
        self._create_file('src/middlewares/errorHandler.ts', self._get_error_handler_content())
        self._create_file('.env', self._get_env_content())
        self._create_file('.gitignore', self._get_gitignore_content())

    def _create_file(self, path: str, content: str):
        full_path = os.path.join(self.project_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content.strip() + '\n')

    def _install_dependencies(self):
        os.chdir(self.project_path)
        os.system('pnpm install')
        print("Dependencies installed successfully!")

    def _generate_prisma_client(self):
        os.chdir(self.project_path)
        os.system('pnpm prisma generate')
        print("Prisma client generated successfully!")

    def _copy_script(self):
        current_script = os.path.abspath(__file__)
        destination = os.path.join(self.project_path, 'express_project_generator.py')
        shutil.copy2(current_script, destination)


    def _get_app_content(self):
        return """
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import 'express-async-errors';
import errorHandler from './middlewares/error-handler';

const app = express();

app.use(cors());
app.use(helmet());
app.use(express.json());

// Add routes here
// app.use('/api/users', userRoutes);

app.use(errorHandler);

export default app;
"""

    def _get_server_content(self):
        return """
import app from './app';
import { PrismaClient } from '@prisma/client';
import { connectDatabase } from './config/database';

const prisma = new PrismaClient();
const port = process.env.PORT || 3000;

async function startServer() {
  try {
    await connectDatabase();
    app.listen(port, () => {
      console.log(`Server running on http://localhost:${port}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

process.on('SIGINT', async () => {
  await prisma.$disconnect();
  process.exit(0);
});
"""
    def _get_error_handler_content(self):
        return """
import { Request, Response, NextFunction } from 'express';

const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);

  res.status(500).json({
    success: false,
    message: 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { error: err.message, stack: err.stack })
  });
};

export default errorHandler;
"""

    def _get_database_config_content(self):
        return """
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function connectDatabase() {
  try {
    await prisma.$connect();
    console.log('Database connected successfully');
  } catch (error) {
    console.error('Database connection failed:', error);
    process.exit(1);
  }
}

export { prisma };
"""

    def _get_error_handler_content(self):
        return """
import { Request, Response, NextFunction } from 'express';

const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);

  res.status(500).json({
    message: 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { error: err.message })
  });
};

export default errorHandler;
"""

    def _get_env_content(self):
        return f"""
PORT=3000
DATABASE_URL="{self.database_url}"
NODE_ENV=development
"""

    def _get_gitignore_content(self):
        return """
node_modules
dist
.env
*.log
"""
def create_module(project_path: str, module_name: str):
    base_path = os.path.join(project_path, 'src')
    
    # Create service
    service_content = f"""
import {{ prisma }} from '../config/database';

export const get{module_name.capitalize()}s = async () => {{
  return prisma.{module_name.lower()}.findMany();
}};

export const get{module_name.capitalize()}ById = async (id: number) => {{
  const {module_name.lower()} = await prisma.{module_name.lower()}.findUnique({{ where: {{ id }} }});
  if (!{module_name.lower()}) {{
    throw new Error('{module_name.capitalize()} not found');
  }}
  return {module_name.lower()};
}};

export const create{module_name.capitalize()} = async (data: any) => {{
  return prisma.{module_name.lower()}.create({{ data }});
}};

export const update{module_name.capitalize()} = async (id: number, data: any) => {{
  const updated{module_name.capitalize()} = await prisma.{module_name.lower()}.update({{ where: {{ id }}, data }});
  if (!updated{module_name.capitalize()}) {{
    throw new Error('{module_name.capitalize()} not found');
  }}
  return updated{module_name.capitalize()};
}};

export const delete{module_name.capitalize()} = async (id: number) => {{
  const deleted{module_name.capitalize()} = await prisma.{module_name.lower()}.delete({{ where: {{ id }} }});
  if (!deleted{module_name.capitalize()}) {{
    throw new Error('{module_name.capitalize()} not found');
  }}
  return deleted{module_name.capitalize()};
}};
"""
    with open(os.path.join(base_path, 'services', f'{module_name.lower()}-service.ts'), 'w') as f:
        f.write(service_content)

    # Create controller
    controller_content = f"""
import {{ Request, Response }} from 'express';
import * as {module_name}Service from '../services/{module_name.lower()}-service';

export const get{module_name.capitalize()}s = async (req: Request, res: Response) => {{
  try {{
    const {module_name}s = await {module_name}Service.get{module_name.capitalize()}s();
    res.json({{ success: true, data: {module_name}s }});
  }} catch (error) {{
    res.status(500).json({{ success: false, message: 'Failed to retrieve {module_name}s', error: error.message }});
  }}
}};

export const get{module_name.capitalize()} = async (req: Request, res: Response) => {{
  try {{
    const {{ id }} = req.params;
    const {module_name} = await {module_name}Service.get{module_name.capitalize()}ById(Number(id));
    res.json({{ success: true, data: {module_name} }});
  }} catch (error) {{
    if (error.message === '{module_name.capitalize()} not found') {{
      res.status(404).json({{ success: false, message: error.message }});
    }} else {{
      res.status(500).json({{ success: false, message: 'Failed to retrieve {module_name}', error: error.message }});
    }}
  }}
}};

export const create{module_name.capitalize()} = async (req: Request, res: Response) => {{
  try {{
    const new{module_name.capitalize()} = await {module_name}Service.create{module_name.capitalize()}(req.body);
    res.status(201).json({{ success: true, data: new{module_name.capitalize()}, message: '{module_name.capitalize()} created successfully' }});
  }} catch (error) {{
    res.status(500).json({{ success: false, message: 'Failed to create {module_name}', error: error.message }});
  }}
}};

export const update{module_name.capitalize()} = async (req: Request, res: Response) => {{
  try {{
    const {{ id }} = req.params;
    const updated{module_name.capitalize()} = await {module_name}Service.update{module_name.capitalize()}(Number(id), req.body);
    res.json({{ success: true, data: updated{module_name.capitalize()}, message: '{module_name.capitalize()} updated successfully' }});
  }} catch (error) {{
    if (error.message === '{module_name.capitalize()} not found') {{
      res.status(404).json({{ success: false, message: error.message }});
    }} else {{
      res.status(500).json({{ success: false, message: 'Failed to update {module_name}', error: error.message }});
    }}
  }}
}};

export const delete{module_name.capitalize()} = async (req: Request, res: Response) => {{
  try {{
    const {{ id }} = req.params;
    await {module_name}Service.delete{module_name.capitalize()}(Number(id));
    res.json({{ success: true, message: '{module_name.capitalize()} deleted successfully' }});
  }} catch (error) {{
    if (error.message === '{module_name.capitalize()} not found') {{
      res.status(404).json({{ success: false, message: error.message }});
    }} else {{
      res.status(500).json({{ success: false, message: 'Failed to delete {module_name}', error: error.message }});
    }}
  }}
}};
"""
    with open(os.path.join(base_path, 'controllers', f'{module_name.lower()}-controller.ts'), 'w') as f:
        f.write(controller_content)

    # Create route
    route_content = f"""
import {{ Router }} from 'express';
import * as {module_name}Controller from '../controllers/{module_name.lower()}-controller';

const router = Router();

router.get('/', {module_name}Controller.get{module_name.capitalize()}s);
router.get('/:id', {module_name}Controller.get{module_name.capitalize()});
router.post('/', {module_name}Controller.create{module_name.capitalize()});
router.put('/:id', {module_name}Controller.update{module_name.capitalize()});
router.delete('/:id', {module_name}Controller.delete{module_name.capitalize()});

export default router;
"""
    with open(os.path.join(base_path, 'routes', f'{module_name.lower()}-routes.ts'), 'w') as f:
        f.write(route_content)

    print(f"{module_name.capitalize()} module created successfully!")

def save_ts_files_to_file(project_path: str):
    src_path = os.path.join(project_path, 'src')
    all_content = []

    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith('.ts'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                with open(file_path, 'r') as f:
                    content = f.read()
                all_content.append(f"// {relative_path}\n\n{content}\n\n{'=' * 80}\n")

    output_file = os.path.join(project_path, 'allcodebase.txt')
    with open(output_file, 'w') as f:
        f.write('\n'.join(all_content))
    
    print(f"All TypeScript files from {src_path} have been saved to {output_file}.")


def main():
    while True:
        print("\n--- Express Project Generator ---")
        print("1. Create New Project")
        print("2. Add New Module to Existing Project")
        print("3. Save All TypeScript Files to allcodebase.txt")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            project_name = input("Enter project name: ")
            generator = ExpressProjectGenerator(project_name)
            generator.create_project()
        elif choice == '2':
            project_path = input("Enter the path to your existing project: ")
            module_name = input("Enter the name of the new module: ")
            create_module(project_path, module_name)
        elif choice == '3':
            project_path = input("Enter the path to your existing project: ")
            save_ts_files_to_file(project_path)
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()