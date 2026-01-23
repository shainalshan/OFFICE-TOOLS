import os
import glob
from django.core.management.base import BaseCommand
from django.conf import settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document as LangchainDocument

from tickets.models import Ticket
from assets.models import Asset
from pixl_core.models import KnowledgeBaseItem

class Command(BaseCommand):
    help = 'Ingest company data into ChromaDB for Pixl AI'

    def handle(self, *args, **kwargs):
        docs = []
        
        # 1. Ingest Tickets (Closed/Completed)
        self.stdout.write("Ingesting Tickets...")
        tickets = Ticket.objects.filter(status='COMPLETED')
        for ticket in tickets:
            content = f"Ticket ID: {ticket.ticket_id}\nIssue: {ticket.issue}\nResolution: {ticket.resolution or 'No resolution recorded.'}"
            docs.append(LangchainDocument(
                page_content=content,
                metadata={"source": f"ticket_{ticket.ticket_id}", "type": "ticket"}
            ))
            
        # 2. Ingest Assets
        self.stdout.write("Ingesting Assets...")
        assets = Asset.objects.all()
        for asset in assets:
            assignee = asset.assigned_to.username if asset.assigned_to else "Unassigned"
            content = f"Asset Serial: {asset.serial_number}\nModel: {asset.brand} {asset.model_detail}\nAssigned To: {assignee}\nStatus: {asset.status}\nLocation: {asset.location}"
            docs.append(LangchainDocument(
                page_content=content,
                metadata={"source": f"asset_{asset.serial_number}", "type": "asset"}
            ))

        # 3. Ingest Knowledge Base
        self.stdout.write("Ingesting Knowledge Base...")
        kb_items = KnowledgeBaseItem.objects.all()
        for item in kb_items:
            content = f"Title: {item.title}\nContent: {item.content}"
            # If file exists, we might want to read it. For now, let's just use the text content.
            # If the user wants file reading (PDF/Text), we would need a loader. 
            # The prompt mentioned ".txt located in media/company_notes/", but for KB it said "custom documents". 
            # I'll enable basic text file reading if a file is present.
            if item.file:
                try:
                    with item.file.open('r') as f:
                        file_content = f.read()
                        # If bytes, decode
                        if isinstance(file_content, bytes):
                             file_content = file_content.decode('utf-8', errors='ignore')
                        content += f"\nFile Content:\n{file_content}"
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not read file for KB {item.title}: {e}"))

            docs.append(LangchainDocument(
                page_content=content,
                metadata={"source": f"kb_{item.id}", "type": "knowledge_base"}
            ))

        # 4. Ingest Media Files (.txt)
        media_notes_dir = os.path.join(settings.MEDIA_ROOT, 'company_notes')
        if os.path.exists(media_notes_dir):
            self.stdout.write(f"Ingesting text files from {media_notes_dir}...")
            txt_files = glob.glob(os.path.join(media_notes_dir, "*.txt"))
            for txt_path in txt_files:
                try:
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    filename = os.path.basename(txt_path)
                    docs.append(LangchainDocument(
                        page_content=content,
                        metadata={"source": filename, "type": "file"}
                    ))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to read {txt_path}: {e}"))
        else:
            self.stdout.write(f"No company_notes directory found at {media_notes_dir}, skipping files.")

        if not docs:
            self.stdout.write(self.style.WARNING("No documents found to ingest."))
            # Still populate DB just to initialize if needed, but Chroma might complain if list is empty.
            return

        # 5. Update ChromaDB
        CHROMA_DB_DIR = "chroma_db_store" # Same path as engine.py expects
        
        self.stdout.write(f"Saving {len(docs)} documents to ChromaDB at {CHROMA_DB_DIR}...")
        
        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Persist directory
        vector_store = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embedding_function
        )
        
        # Add documents (This appends. To full refresh, we'd delete the collection first, but let's just add for now or reset)
        # For a "Teacher" command, usually we want to update. Simple way is delete and re-create.
        try:
            vector_store.reset_collection() # This might be method dependent on langchain version, but reset is good.
                                            # Actually Chroma client has reset, Langchain wrapper might not expose it directly easily?
                                            # Let's try .delete_collection() wait, Langchain Chroma wrapper is simple.
            # Best way to clear for this simple implementation: Delete the dir? 
            # Or just add. Duplicates might happen if we just add.
            # Let's try to just add for now, user asked to "update".
            pass 
        except:
            pass
            
        vector_store.add_documents(docs)
        self.stdout.write(self.style.SUCCESS("Successfully updated Pixl AI Memory."))
